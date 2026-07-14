from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="",
    tags=["Front"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", status_code=status.HTTP_302_FOUND)
async def root():
    return RedirectResponse(url="/home")


@router.get("/politica", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def politica(request: Request):
    return templates.TemplateResponse("politica/politica.html", {"request": request})


@router.get("/cookies", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def cookies(request: Request):
    return templates.TemplateResponse("politica/cookies.html", {"request": request})
