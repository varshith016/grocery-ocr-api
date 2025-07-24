# sample_client.py

import requests
import json

# --- Configuration (UPDATED) ---
API_URL = "http://127.0.0.1:8000/v1/extract_items"
IMAGE_PATH = "D:\\Internship Project -1\\ai-ocr_receipts\\images\\1.jpg"  # <-- IMPORTANT: Change this to the path of your test image
API_KEY = "meallens@ocr"            # <-- Your new password
API_KEY_NAME = "ocr-api"            # <-- Your new header name

def call_receipt_api(image_path: str):
    """
    Sends an image to the protected API and prints the response.
    """
    print(f"Attempting to process image: {image_path}")

    # 1. Set the required headers with the new API key and name
    headers = {
        API_KEY_NAME: API_KEY,
        "accept": "application/json",
    }

    # 2. Open the image file in binary read mode
    try:
        with open(image_path, "rb") as image_file:
            files = {
                "image": (image_file.name, image_file, "image/jpeg")
            }

            # 3. Send the POST request
            print("Sending request to API...")
            response = requests.post(API_URL, headers=headers, files=files)

            # 4. Check the response from the server
            if response.status_code == 200:
                print("\n✅ Success! API Response:")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"\n❌ Error: Received status code {response.status_code}")
                print("Response content:", response.text)

    except FileNotFoundError:
        print(f"\n❌ Error: The file was not found at path: {image_path}")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: A connection error occurred: {e}")

if __name__ == "__main__":
    call_receipt_api(IMAGE_PATH)
