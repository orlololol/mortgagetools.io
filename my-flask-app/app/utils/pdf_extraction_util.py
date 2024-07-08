import fitz  # PyMuPDF
import re

def extract_text(pdf_path, coords, page_number):
    """Extract text from specified coordinates and page."""
    document = fitz.open(pdf_path)
    page = document.load_page(page_number)
    rect = fitz.Rect(coords)
    text = page.get_textbox(rect)
    document.close()
    return text.strip()

def extract_amortization_value(text_block):
    """Extracts the monetary value for lines containing 'Amortization' or 'Casualty' followed by 'Loss'."""
    lines = text_block.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'\bamortization\b', line, re.IGNORECASE) and re.search(r'\bloss\b', line, re.IGNORECASE) or \
           re.search(r'\bcasualty\b', line, re.IGNORECASE) and re.search(r'\bloss\b', line, re.IGNORECASE):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                matches = re.findall(r'\d+[\.,\d+]*', next_line)
                if matches:
                    return matches[0].replace(',', '').replace('.', '')
    return None
