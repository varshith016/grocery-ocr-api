# Grocery Receipt OCR API – Deployment & Usage Documentation

## Overview
This API extracts grocery items from receipt images using OCR.  
It is deployed and running live on Hugging Face Spaces.

- **Base URL:**  
  [https://varshith016-grocery-ocr-api.hf.space/](https://varshith016-grocery-ocr-api.hf.space/)

---

## Endpoints

### 1. Health Check
- **GET /**  
  Returns a simple message to confirm the API is online.

  **Example Response:**
  ```json
  {"message": "API is online. Go to /docs for documentation."}
  ```

---

### 2. Extract Grocery Items
- **POST /v1/extract_items**
- **Description:** Upload a receipt image (JPG/PNG) to extract grocery items.
- **Authentication:**  
  Requires API key in the header:  
  `ocr-api: meallens@ocr`
- **Request:**  
  - Content-Type: multipart/form-data
  - Form field: `image` (the image file)
- **Response:**  
  Returns a list of extracted grocery items with confidence scores.
  **Example Response:**
  ```json
  [
    {
      "id": 1,
      "name": "Fresh Bananas",
      "confidence": 95,
      "amount": "6",
      "unit": "pieces"
    },
    ...
  ]
  ```
---
## Interactive API Documentation
- **Swagger UI:**  
  [https://varshith016-grocery-ocr-api.hf.space/docs](https://varshith016-grocery-ocr-api.hf.space/docs)  
  Use this to interactively test the API and see request/response formats.
---
## Example Usage (with curl)
```sh
curl -X POST "https://varshith016-grocery-ocr-api.hf.space/v1/extract_items" \
  -H "ocr-api: meallens@ocr" \
  -F "image=@/path/to/your/receipt.jpg"
```
Replace `/path/to/your/receipt.jpg` with the path to your image file.
---
## Deployment Details
- **Platform:** Hugging Face Spaces (Docker)
- **OCR Engine:** Tesseract (installed in the Docker container)
- **API Framework:** FastAPI (Python)
- **Status:** Online and available 24/7

---

## Notes

- The API is cloud-hosted and available at all times.
- For any changes or updates, push to the Hugging Face Space repository.
- For further details, see the `/docs` endpoint.
