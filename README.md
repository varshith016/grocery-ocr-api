# Grocery Receipt OCR API (FastAPI)

This project is a FastAPI-based API for extracting grocery items from receipt images using OCR.

## Endpoints

### Health Check
- `GET /` — Returns a simple health check response.

### Extract Grocery Items
- `POST /v1/extract_items`
  - Accepts: Image file (JPG/PNG) as form-data
  - Requires header: `ocr-api: meallens@ocr`
  - Returns: List of extracted grocery items with confidence scores

## API Key Authentication
All requests to `/v1/extract_items` must include the following header:
```
ocr-api: meallens@ocr
```

## Example Usage (with curl)
```bash
curl -X POST "https://<your-space-name>.hf.space/v1/extract_items" \
  -H  "ocr-api: meallens@ocr" \
  -H  "accept: application/json" \
  -H  "Content-Type: multipart/form-data" \
  -F "image=@/path/to/your/receipt.jpg"
```

## Interactive API Docs
Once deployed, visit:
```
https://<your-space-name>.hf.space/docs
```
for interactive Swagger UI documentation.

## Deployment
This app is deployed on Hugging Face Spaces using Docker and runs on port 7860 as required by Spaces. 