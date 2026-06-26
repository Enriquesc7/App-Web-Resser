# Project Context - App Web Resser

This project is a web application focused on recycling and plastic packaging analysis.

## Tech stack

* Backend: FastAPI
* Database: PostgreSQL
* ORM: SQLAlchemy
* Frontend: HTML, CSS and vanilla JavaScript
* Environment variables are managed with `.env`
* Do not migrate the project to React, Vue or another frontend framework.
* Do not replace SQLAlchemy with another ORM.
* Preserve the current project structure unless a change is clearly necessary.

## Current core functionality

The application allows users to scan or search products and obtain information about:

* Type of plastic used in the package
* Approximate quantity of plastic
* Whether the package is recyclable
* Recycling/environmental guidance

The application is mainly focused on plastic products and plastic packaging. Cans, glass and other materials may be detected later, but they are not the main scope.

## New feature to implement

Add a new feature that allows the user to scan or upload a supermarket receipt image. The system should process the receipt, extract the purchased products and estimate the amount/type of plastic packaging consumed by the user.

Expected flow:

1. User opens the app.
2. User scans a receipt or uploads an image.
3. The backend receives the image.
4. The system improves the image when possible:

   * crop
   * contrast
   * orientation
   * basic noise reduction
5. OCR extracts text from the receipt.
6. The backend parses and structures the receipt data:

   * product names
   * quantities
   * possible prices if available
7. The system normalizes abbreviated product names.
   Example:
   `BEB CC 1.5 LT` → `Coca-Cola bottle 1.5 L`
8. The system searches for product matches using:

   * the existing local database
   * barcode data if available
   * external sources such as Open Food Facts when appropriate
9. The system estimates the likely package:

   * PET bottle
   * PP container
   * flexible plastic bag
   * multilayer carton
   * glass
   * can
   * unknown
10. The system estimates:

* likely plastic type
* approximate packaging weight in grams
* recyclability
* confidence level

11. The frontend displays the results to the user.

## Development rules

Before coding:

* Inspect the existing project structure.
* Identify the current models, routers, schemas, utilities and frontend files.
* Propose an implementation plan.
* Do not modify existing functionality unless required.
* Avoid large rewrites.
* Implement the feature incrementally.

Backend preferences:

* Use FastAPI routers.
* Use SQLAlchemy models.
* Use Pydantic schemas compatible with the existing FastAPI/Pydantic version.
* Keep OCR, parsing, normalization, product matching and impact estimation as separate service modules.
* Use clear names and comments where useful.

Database preferences:

* Do not run destructive migrations.
* Propose new tables before creating them.
* Prefer additive changes.
* Suggested entities may include:

  * receipt_scans
  * receipt_items
  * receipt_item_matches
  * packaging_estimates

Frontend preferences:

* Use existing HTML/CSS/JavaScript structure.
* Add a simple upload/scan interface.
* Show loading status while the receipt is processed.
* Show results in a clear table or cards.
* Show confidence level and allow uncertain products to be marked as “needs review”.

Expected MVP:

* Upload receipt image.
* Run OCR.
* Extract raw receipt lines.
* Detect probable product lines.
* Save scan and detected items.
* Return structured JSON.
* Display results in the frontend.
* Use a simple rule-based packaging estimation when product match is uncertain.

Do not implement advanced AI integration until the basic pipeline works.
