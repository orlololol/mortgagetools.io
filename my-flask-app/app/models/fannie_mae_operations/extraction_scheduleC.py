from ...utils.pdf_extraction_util import extract_text, extract_amortization_value
from ...utils.google_sheets_util import SheetPopulatorWithoutAI
from ...config import get_config
import os
import fitz  # PyMuPDF
import re

# Get the current environment ('development', 'testing', 'production')
env = os.getenv('APP_ENV', 'default')

# Get the configuration for the current environment
config = get_config(env)

def extract_text(pdf_path, coords, page_number):
    """Extract text from specified coordinates and page."""
    document = fitz.open(pdf_path)
    page = document.load_page(page_number)
    rect = fitz.Rect(coords)
    text = page.get_textbox(rect)
    document.close()
    print(f"Extracted text: {text.strip()}")
    return text.strip()

def extract_amortization_value(text_block):
    """Extracts the monetary value for lines containing 'Amortization' or 'Casualty' followed by 'Loss'."""
    lines = text_block.split('\n')
    for i, line in enumerate(lines):
        # Check for the presence of keywords in the current line
        if re.search(r'\bamortization\b', line, re.IGNORECASE) and re.search(r'\bloss\b', line, re.IGNORECASE) or \
           re.search(r'\bcasualty\b', line, re.IGNORECASE) and re.search(r'\bloss\b', line, re.IGNORECASE):
            # Check if the next line exists and extract the monetary value
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                matches = re.findall(r'\d+[\.,\d+]*', next_line)
                if matches:
                    # Return the first match, removing commas and periods for clean numeric value
                    return matches[0].replace(',', '').replace('.', '')
    return None

def extract_data(coords_page_1, coords_page_2, pdf_path):
    extracted_data = {}
    # Extract data from page 1
    for key, rect in coords_page_1.items():
        print(f"Extracting data for {key}")
        extracted_data[key] = extract_text(pdf_path, rect, 0)

    # Extract data from page 2
    for key, rect in coords_page_2.items():
        text_block = extract_text(pdf_path, rect, 1)
        if key == "part5":
            extracted_data[key] = extract_amortization_value(text_block)
        else:
            extracted_data[key] = text_block
    return extracted_data

def scheduleC_extractor(pdf_path, spreadsheet_id):
    coords_page_1 = {
        "line6": (477, 325, 576, 334),
        "line12": (195, 421, 295, 431),
        "line13": (196, 434, 294, 467),
        "line30": (476, 577, 576, 634),
        "line31": (476, 638, 577, 670),
        "line24b": (477, 490, 574, 500)
    }
    coords_page_2 = {
        "line44a": (104, 408, 201, 418),
        "part5": (35, 532, 576, 742)
    }
    cell_map = {
        "line6": "G17",
        "line12": "G18",
        "line13": "G19",
        "line30": "G21",
        "line31": "G16",
        "line24b": "G20",
        "line44a": "G23",
        "part5": "G22"
    }

    extracted_data = extract_data(coords_page_1, coords_page_2, pdf_path)
    print(f"Extracted data: {extracted_data}")
    
    google_sheets_credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    google_sheets_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing'

    # Populate the Google Sheet
    google_sheet_populator = SheetPopulatorWithoutAI(google_sheets_credentials, google_sheets_url)
    google_sheet_populator.populate_sheet_without_ai(extracted_data, cell_map)

