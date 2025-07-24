import streamlit as st
from PIL import Image
import os
import tempfile
import json
from extracted_items import extract_grocery_items

st.set_page_config(page_title="Receipt Grocery Item Extractor", layout="centered")
st.title("🧾 Receipt Grocery Item Extractor")
st.write("""
Upload a photo of your grocery receipt. The app will extract the list of items and their quantities for you!
""")

uploaded_file = st.file_uploader("Choose a receipt image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        # Display the uploaded image
        st.image(tmp_path, caption="Uploaded Receipt", use_container_width=True)
        # Extract items
        with st.spinner("Extracting items from receipt..."):
            result = extract_grocery_items(tmp_path)
        # Remove temp file
        os.remove(tmp_path)
        # Show result
        if isinstance(result, list):
            if result:
                st.success(f"Extracted {len(result)} item(s) from the receipt:")
                st.dataframe(result)
                st.json({"items": result})
            else:
                st.warning("No items found on the receipt.")
        else:
            st.error(result)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload a receipt image to get started.") 