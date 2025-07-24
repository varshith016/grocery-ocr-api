# extract_items.py

import pytesseract
import re
import json
from PIL import Image


# --- Configuration ---
# On Windows, you must tell pytesseract where you installed Tesseract.
# Update this path to where your tesseract.exe is located.
# On Mac/Linux, you can usually leave this commented out.
# For example: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# The path to the receipt image you want to process.
IMAGE_PATH = "./Receipts/11.jpeg" # <-- CHANGE THIS to your image file

def normalize_unit(unit):
    """
    Normalize unit variations to standard forms.
    """
    unit_lower = unit.lower().strip()
    
    # Weight units
    if unit_lower in ['g', 'gram', 'grams']:
        return 'g'
    elif unit_lower in ['kg', 'kq', 'kilogram', 'kilograms']:
        return 'kg'
    elif unit_lower in ['lbs', 'lb', 'pound', 'pounds']:
        return 'lbs'
    elif unit_lower in ['oz', 'ounce', 'ounces']:
        return 'oz'
    
    # Volume units
    elif unit_lower in ['l', 'liter', 'liters', 'litre', 'litres']:
        return 'l'
    elif unit_lower in ['ml', 'milliliter', 'milliliters']:
        return 'ml'
    elif unit_lower in ['fl oz', 'floz']:
        return 'fl oz'
    
    # Count units
    elif unit_lower in ['each', 'pc', 'pcs', 'piece', 'pieces', 'unit', 'units']:
        return 'each'
    
    # Default
    return unit_lower

def get_default_unit(item_name):
    """
    Intelligently determine the default unit based on the item name.
    """
    item_lower = item_name.lower()
    
    # Weight-based items
    weight_keywords = ['flour', 'sugar', 'salt', 'pepper', 'spice', 'herb', 'meat', 'chicken', 'beef', 'pork', 'fish', 'vegetable', 'fruit', 'apple', 'banana', 'tomato', 'potato', 'onion', 'carrot', 'lettuce', 'spinach', 'cheese', 'butter', 'oil', 'sauce', 'dressing', 'powder', 'grain', 'rice', 'pasta', 'bean', 'nut', 'seed']
    for keyword in weight_keywords:
        if keyword in item_lower:
            return 'kg'
    
    # Volume-based items
    volume_keywords = ['milk', 'water', 'juice', 'soda', 'beer', 'wine', 'oil', 'vinegar', 'sauce', 'soup', 'broth', 'liquid', 'drink', 'beverage']
    for keyword in volume_keywords:
        if keyword in item_lower:
            return 'l'
    
    # Count-based items (default)
    return 'each'

def extract_grocery_items(image_path):
    """
    Extracts text from a receipt image using Tesseract and parses grocery items.
    """
    try:
        # 1. Use Tesseract to extract all text from the image
        img = Image.open(image_path)
        full_text = pytesseract.image_to_string(img)
        lines = full_text.split('\n')

        # Receipt validation logic: check for common receipt keywords
        receipt_keywords = ["total", "subtotal", "cash", "change", "kg", "each", "price", "item", "date", "store", "receipt", "quantity"]
        text = ' '.join(lines).lower()
        if not any(k in text for k in receipt_keywords):
            return "This does not appear to be a receipt. Please upload a proper receipt image."

        extracted_items = []
        # Comprehensive list of keywords to skip (non-grocery items)
        skip_keywords = [
            # Receipt metadata
            "special", "subtotal", "loyalty", "total", "cash", "change", "@", "net", "date", "time",
            "receipt", "thank", "shopping", "store", "address", "phone", "fax", "www", "com", "org",
            "open", "closed", "hours", "daily", "weekly", "tax", "taxable", "non-taxable",
            "items", "count", "register", "transaction", "card", "debit", "credit", "pin",
            "signature", "authorized", "approved", "declined", "balance", "due", "paid",
            "refund", "return", "exchange", "discount", "sale", "clearance", "coupon",
            "member", "customer", "account", "number", "id", "employee", "cashier",
            "manager", "supervisor", "assistant", "help", "service", "support",
            # Common receipt headers/footers
            "welcome", "goodbye", "come again", "visit", "location", "branch",
            "headquarters", "corporate", "office", "main", "north", "south", "east", "west",
            "street", "avenue", "road", "drive", "lane", "boulevard", "highway",
            "suite", "apartment", "floor", "building", "center", "mall", "plaza",
            "parking", "entrance", "exit", "restroom", "elevator", "escalator",
            # Time and date patterns
            "am", "pm", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december",
            # Phone and contact patterns
            "tel", "telephone", "call", "contact", "email", "website", "web", "online",
            # Common receipt text
            "original", "copy", "duplicate", "void", "cancelled", "refunded", "returned",
            "sold", "bought", "purchased", "bought", "sale", "buy", "sell", "price", "cost",
            "amount", "value", "worth", "expensive", "cheap", "affordable", "budget",
            "save", "savings", "money", "dollar", "cent", "penny", "nickel", "dime", "quarter"
        ]
        
        # Enhanced unit detection patterns
        # Common weight units: kg, g, grams, lbs, pounds, oz, ounces
        # Common volume units: l, liters, ml, milliliters, fl oz
        # Common count units: each, pcs, pieces, units
        weight_units = r'(kg|kq|g|grams?|lbs?|pounds?|oz|ounces?)'
        volume_units = r'(l|liters?|ml|milliliters?|fl\s*oz)'
        count_units = r'(each|pcs?|pieces?|units?)'
        all_units = f'({weight_units}|{volume_units}|{count_units})'
        
        name_price_pattern = re.compile(r'^(.+?)\s+\$?([\d.]+)$')
        qty_line_pattern = re.compile(f'([\d.]+)\\s*{all_units}', re.IGNORECASE)
        # Pattern: item name, quantity, price (e.g., Milk 1 1.89)
        name_qty_price_pattern = re.compile(r'^(.*?)\s+(\d+)\s+([\d.]+)$')
        # Pattern: item name, quantity, unit (e.g., ZUCHINNI GREEN 0.778 kg)
        name_qty_unit_pattern = re.compile(f'^(.*?)\\s+([\d.]+)\\s*{all_units}$', re.IGNORECASE)
        # Pattern: item name, quantity (e.g., Eggs 1)
        name_qty_pattern = re.compile(r'^(.*?)\s+(\d+)$')
        quantity_line_pattern = re.compile(f'Quantity:\\s*(\\d+)\\s*x\\s*([\d.]+)\\s*{all_units}?', re.IGNORECASE)
        
        # Pattern: item name with embedded quantity and unit (e.g., "2kg flour", "500g sugar")
        embedded_qty_unit_pattern = re.compile(f'^([\d.]+){all_units}\\s+(.+)$', re.IGNORECASE)

        # To accumulate items by name for summing quantities
        item_accumulator = {}

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Handle two-line item format: previous line is item name, current line is quantity/price/unit
            if line.lower().startswith('quantity:'):
                qty_match = quantity_line_pattern.match(line)
                if qty_match and i > 0:
                    item_name = lines[i-1].strip()
                    quantity = float(qty_match.group(1))
                    unit = normalize_unit(qty_match.group(3)) if qty_match.group(3) else 'each'
                    key = (item_name.lower(), unit)
                    item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                i += 1
                continue
            if not line or any(k in line.lower() for k in skip_keywords):
                i += 1
                continue
                
            # 0. Check for embedded quantity and unit in item name (e.g., "2kg flour", "500g sugar")
            embedded_match = embedded_qty_unit_pattern.match(line)
            if embedded_match:
                quantity = float(embedded_match.group(1))
                unit = normalize_unit(embedded_match.group(2))
                item_name = embedded_match.group(3).strip()
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                i += 1
                continue
            # 1. Item name + price, then quantity/unit on next line
            name_price_match = name_price_pattern.match(line)
            if name_price_match:
                item_name = name_price_match.group(1).strip()
                quantity = 1
                unit = get_default_unit(item_name)  # Use intelligent default
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    qty_match = qty_line_pattern.search(next_line)
                    if qty_match:
                        quantity = float(qty_match.group(1))
                        unit = normalize_unit(qty_match.group(2))
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                continue
            # 2. Item name, quantity, price (all on one line)
            name_qty_price_match = name_qty_price_pattern.match(line)
            if name_qty_price_match:
                item_name = name_qty_price_match.group(1).strip()
                quantity = float(name_qty_price_match.group(2))
                unit = get_default_unit(item_name)  # Use intelligent default
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                i += 1
                continue
            # 3. Item name, quantity, unit (all on one line)
            name_qty_unit_match = name_qty_unit_pattern.match(line)
            if name_qty_unit_match:
                item_name = name_qty_unit_match.group(1).strip()
                quantity = float(name_qty_unit_match.group(2))
                unit = normalize_unit(name_qty_unit_match.group(3))
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                i += 1
                continue
            # 4. Item name and quantity (all on one line)
            name_qty_match = name_qty_pattern.match(line)
            if name_qty_match:
                item_name = name_qty_match.group(1).strip()
                quantity = float(name_qty_match.group(2))
                unit = get_default_unit(item_name)  # Use intelligent default
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
                i += 1
                continue
            # 5. Item name only (likely with price, no quantity/unit)
            # Try to match lines that look like an item name (not a keyword, not empty, not a header)
            if len(line.split()) > 1 and not any(k in line.lower() for k in skip_keywords):
                item_name = line.strip()
                quantity = 1
                unit = get_default_unit(item_name)  # Use intelligent default
                key = (item_name.lower(), unit)
                item_accumulator[key] = item_accumulator.get(key, 0) + quantity
            i += 1

        # Convert accumulator to output format
        extracted_items = []
        for k, v in item_accumulator.items():
            item_name = k[0].title()
            unit = k[1]
            # Confidence scoring
            confidence = 0.6  # default
            # High confidence if item name contains a grocery keyword
            grocery_keywords = [
                'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'raspberry', 'blackberry',
                'peach', 'pear', 'plum', 'cherry', 'apricot', 'nectarine', 'mango', 'pineapple', 'kiwi',
                'tomato', 'potato', 'onion', 'carrot', 'lettuce', 'spinach', 'kale', 'cabbage', 'broccoli',
                'cauliflower', 'cucumber', 'pepper', 'bell', 'jalapeno', 'garlic', 'ginger', 'mushroom',
                'avocado', 'lemon', 'lime', 'grapefruit', 'tangerine', 'clementine', 'mandarin',
                'zucchini', 'squash', 'pumpkin', 'eggplant', 'asparagus', 'celery', 'radish', 'turnip',
                'beet', 'parsnip', 'rutabaga', 'sweet potato', 'yam', 'corn', 'peas', 'beans', 'lentil',
                'milk', 'cheese', 'yogurt', 'cream', 'butter', 'egg', 'eggs', 'cream cheese', 'cottage',
                'sour cream', 'half and half', 'heavy cream', 'whipping cream', 'buttermilk',
                'chicken', 'beef', 'pork', 'lamb', 'turkey', 'duck', 'fish', 'salmon', 'tuna', 'cod',
                'shrimp', 'crab', 'lobster', 'bacon', 'sausage', 'ham', 'steak', 'ground', 'burger',
                'hot dog', 'hotdog', 'deli', 'lunch meat', 'cold cut',
                'bread', 'wheat', 'white', 'rye', 'sourdough', 'bagel', 'muffin', 'croissant', 'roll',
                'tortilla', 'pita', 'naan', 'rice', 'pasta', 'noodle', 'spaghetti', 'penne', 'macaroni',
                'couscous', 'quinoa', 'oatmeal', 'cereal', 'granola', 'flour', 'sugar', 'salt', 'pepper',
                'soup', 'sauce', 'ketchup', 'mustard', 'mayonnaise', 'relish', 'pickle', 'olive',
                'tuna', 'salmon', 'bean', 'corn', 'peas', 'tomato paste', 'tomato sauce', 'broth',
                'stock', 'juice', 'soda', 'pop', 'cola', 'water', 'tea', 'coffee', 'hot chocolate',
                'chip', 'cracker', 'cookie', 'biscuit', 'cake', 'pie', 'brownie', 'muffin', 'donut',
                'candy', 'chocolate', 'gum', 'popcorn', 'pretzel', 'nut', 'almond', 'walnut', 'pecan',
                'cashew', 'peanut', 'sunflower', 'pumpkin seed', 'raisin', 'dried fruit',
                'frozen', 'ice cream', 'pizza', 'dinner', 'meal', 'vegetable', 'fruit',
                'organic', 'natural', 'gluten free', 'vegan', 'vegetarian', 'low fat', 'fat free',
                'sugar free', 'diet', 'light', 'lite', 'fresh', 'local', 'farm', 'artisan'
            ]
            if any(keyword in item_name.lower() for keyword in grocery_keywords):
                confidence = 0.95
            # Higher confidence if unit is not 'each'
            if unit != 'each':
                confidence = max(confidence, 0.85)
            extracted_items.append({
                "item_name": item_name,
                "quantity": v,
                "unit": unit,
                "confidence": confidence
            })

        return extracted_items

    except FileNotFoundError:
        return f"Error: The file '{image_path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    items = extract_grocery_items(IMAGE_PATH)
    
    if isinstance(items, list):
        print("--- Extracted Items (JSON) ---")
        # Print the result as a clean JSON object
        print(json.dumps({"items": items}, indent=4))
    else:
        # Print any errors that occurred
        print(items)