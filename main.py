# main.py - FINAL CORRECTED VERSION

from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import List
import os
import uuid
import time

# ==============================================================================
# 1. IMPORT YOUR EXTRACTION FUNCTION
# ==============================================================================
from extracted_items import extract_grocery_items

# ==============================================================================
# 2. API KEY SECURITY SETUP
# ==============================================================================
API_KEY = "meallens@ocr"
API_KEY_NAME = "ocr-api"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """Dependency to validate the API key."""
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate credentials"
        )

# ==============================================================================
# 3. DEFINE THE FINAL RESPONSE MODEL
# ==============================================================================
class GroceryItem(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="Fresh Bananas")
    confidence: int = Field(..., example=95, description="Confidence score from 0 to 100")
    amount: str = Field(..., example="6")
    unit: str = Field(..., example="pieces")


# ==============================================================================
# 4. INITIALIZE THE FastAPI APP
# ==============================================================================
app = FastAPI(
    title="Grocery Receipt API",
    version="2.3-stable",
    description="""
    An API to extract items from a grocery receipt image.

    **Authentication**:
    To use this API, you must include an API key in the request headers.
    - Header Name: `ocr-api`
    - Header Value: `meallens@ocr`
    """,
    contact={
        "name": "Foysal Rahman",
        "email": "foysal@example.com",
    },
)


# ==============================================================================
# 5. CREATE THE PROTECTED API ENDPOINT
# ==============================================================================
@app.post("/v1/extract_items",
          response_model=List[GroceryItem],
          tags=["Receipt Analysis"],
          dependencies=[Depends(get_api_key)])
async def extract_items_from_receipt(image: UploadFile = File(...)):
    """
    Accepts an image file (JPG/PNG), processes it to find grocery items,
    and returns a structured list of those items. Requires API key authentication.
    """
    temp_filename = f"temp_{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"

    try:
        contents = await image.read()
        with open(temp_filename, "wb") as f:
            f.write(contents)

        extracted_data = extract_grocery_items(temp_filename)
        
        if isinstance(extracted_data, str):
            raise HTTPException(status_code=400, detail=extracted_data)

        formatted_response = []
        for i, item in enumerate(extracted_data):
            # THE FIX IS HERE: Multiply confidence by 100 and round to int
            confidence_score = int(round(float(item.get("confidence", 0)) * 100))
            formatted_response.append({
                "id": i + 1,
                "name": item.get("item_name", "Unknown Item"),
                "confidence": confidence_score,
                "amount": str(item.get("quantity", "0")),
                "unit": item.get("unit", "unknown")
            })

        return formatted_response

    except Exception as e:
        # This will now catch validation errors earlier if they happen
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "API is online. Go to /docs for documentation."}
