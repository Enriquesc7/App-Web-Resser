# FastAPI
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# SQLAlchemy
from sqlalchemy.orm import Session

# App
from utils import get_db
from managers.receipt import ReceiptManager
from managers.auth import get_optional_current_user
from schemas.receipt import ReceiptScanResponse, ReceiptWasteSummary
from schemas import user as user_schema

# Python
from typing import Optional, List


templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/receipt",
    tags=["Receipts"],
    responses={404: {"description": "Not found"}},
)


def _image_path_to_url(image_path: Optional[str]) -> Optional[str]:
    """Convert stored relative path like 'static/uploads/...' to URL '/static/uploads/...'."""
    if not image_path:
        return None
    return "/" + image_path.replace("\\", "/")


@router.get(
    "",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Receipt upload page",
    tags=["Receipts"],
)
async def receipt_page(
    request: Request,
    current_user: Optional[user_schema.User] = Depends(get_optional_current_user),
):
    return templates.TemplateResponse(
        "users/receipt/receipt_upload.html",
        {"request": request, "user": current_user},
    )


# Maximum allowed upload size: 10 MB
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024

# Allowed MIME types
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}


@router.get(
    "/scans",
    status_code=status.HTTP_200_OK,
    summary="Return the 20 most recent receipt scans for the history panel",
)
async def list_receipt_scans(
    db: Session = Depends(get_db),
    current_user: Optional[user_schema.User] = Depends(get_optional_current_user),
):
    from models.receipt import ReceiptScan

    query = db.query(ReceiptScan)
    if current_user is None:
        query = query.filter(ReceiptScan.user_id.is_(None))
    else:
        query = query.filter(ReceiptScan.user_id == current_user.id)

    scans = (
        query
        .order_by(ReceiptScan.created_at.desc())
        .limit(20)
        .all()
    )

    result = []
    for scan in scans:
        item_count = len(scan.items)
        total_plastic = sum(
            (item.estimate.weight_grams or 0)
            for item in scan.items
            if item.estimate
        )
        result.append({
            "scan_id": scan.id,
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "item_count": item_count,
            "total_plastic_grams": round(total_plastic, 1),
            "image_url": _image_path_to_url(scan.image_path),
        })

    return JSONResponse(status_code=200, content=result)


@router.get(
    "/summary",
    response_model=ReceiptWasteSummary,
    status_code=status.HTTP_200_OK,
    summary="Aggregate cumulative waste breakdown and estimated CO2 impact for the current visitor",
)
async def get_receipt_summary(
    db: Session = Depends(get_db),
    current_user: Optional[user_schema.User] = Depends(get_optional_current_user),
):
    # Ownership follows the same rule as /receipt/scans and /receipt/{scan_id}:
    # guests share one bucket (user_id IS NULL) across all anonymous devices.
    # That sharing is an inherited limitation, not a new bug in this endpoint.
    user_id = current_user.id if current_user else None
    summary = ReceiptManager.get_waste_summary(db, user_id)
    return JSONResponse(status_code=200, content=summary)


@router.post(
    "/upload",
    response_model=ReceiptScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a receipt image and extract product/plastic data",
    description=(
        "Accepts a receipt image (JPEG, PNG, WEBP, TIFF). "
        "The image is preprocessed, OCR is applied, product lines are extracted, "
        "and a packaging estimate is returned for each detected item. "
        "If Tesseract OCR is not installed, the scan is saved but items will be empty "
        "and an informational error message is returned."
    ),
)
async def upload_receipt(
    request: Request,
    file: UploadFile = File(..., description="Receipt image file (JPEG, PNG, WEBP or TIFF)"),
    db: Session = Depends(get_db),
    current_user: Optional[user_schema.User] = Depends(get_optional_current_user),
):
    # --- Validate content type ---
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                f"Accepted types: {', '.join(ALLOWED_CONTENT_TYPES)}"
            ),
        )

    # --- Read and validate file size ---
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is {MAX_IMAGE_SIZE_BYTES // (1024*1024)} MB.",
        )

    # --- Run pipeline ---
    try:
        result = ReceiptManager.process_receipt(
            db=db,
            image_bytes=image_bytes,
            original_filename=file.filename or "receipt.jpg",
            user_id=current_user.id if current_user else None,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Receipt processing failed: {str(exc)}",
        )

    # Add image_url to fresh-scan response
    from models.receipt import ReceiptScan
    scan = db.query(ReceiptScan).filter(ReceiptScan.id == result["scan_id"]).first()
    result["image_url"] = _image_path_to_url(scan.image_path) if scan else None

    return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.get(
    "/{scan_id}",
    response_model=ReceiptScanResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a previously processed receipt scan",
)
async def get_receipt_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[user_schema.User] = Depends(get_optional_current_user),
):
    from models.receipt import ReceiptScan

    scan = db.query(ReceiptScan).filter(ReceiptScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")

    # Ownership check — return 404 (not 403) to avoid leaking existence
    if current_user is None:
        if scan.user_id is not None:
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    else:
        if scan.user_id != current_user.id:
            raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")

    items = []
    for item in scan.items:
        est = item.estimate
        items.append({
            "raw_line": item.raw_line,
            "normalized_name": item.normalized_name,
            "brand": None,
            "quantity": item.quantity,
            "unit_price": None,
            "line_total": item.price,
            "size": None,
            "packaging_type": est.packaging_type if est else None,
            "plastic_type": est.plastic_type if est else None,
            "weight_grams": est.weight_grams if est else None,
            "recyclable": est.recyclable if est else None,
            "waste_type": est.waste_type if est else None,
            "confidence": est.confidence if est else None,
            "needs_review": est.needs_review if est else True,
        })

    return JSONResponse(status_code=200, content={
        "scan_id": scan.id,
        "status": scan.status,
        "raw_text": scan.raw_ocr_text,
        "items": items,
        "error": scan.error_message,
        "image_url": _image_path_to_url(scan.image_path),
    })
