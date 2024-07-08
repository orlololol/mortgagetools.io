from ..utils.doc_ai_util import online_process
from ..utils.firestore_util import initialize_firestore, store_data_in_firestore
from ..utils.google_sheets_util import SheetPopulator
from typing import List, Dict, Any
from google.cloud import documentai_v1 as documentai
import json
from ..config import get_config
import os

# Get the current environment ('development', 'testing', 'production')
env = os.getenv('APP_ENV', 'default')

# Get the configuration for the current environment
config = get_config(env)

def extract_data(document: documentai.Document) -> List[Dict[str, Any]]:
    data = []
    for entity in document.entities:
        
        data.append({
            'Type': entity.type_,
            'Raw Value': entity.mention_text,
            'Normalized Value': entity.normalized_value.text,
            'Confidence': f"{entity.confidence:.0%}"
        })

        for prop in entity.properties:
            
            data.append({
                'Type': prop.type_,
                'Raw Value': prop.mention_text,
                'Normalized Value': prop.normalized_value.text,
                'Confidence': f"{prop.confidence:.0%}"
            })
    return data

def paystub_extractor(project_id, location, processor_id, file_path, mime_type, spreadsheet_id):
    """
    Orchestrates the process of extracting data from paystubs.
    Utilizes Google Document AI to process the document, stores the data in Firestore,
    and updates a Google Sheet based on a specific mapping.
    """
    # Process the document using Google Document AI
    document = online_process(project_id, location, processor_id, file_path, mime_type)
    # print(f"Processed document of type {type(document.document)} with attributes {dir(document.document)}")

    # Extract data from the processed document
    data = extract_data(document.document)

    # Save the extracted data to JSON and store in Firestore
    json_file = 'extracted_data.json'  # Define the JSON file name
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

    initialize_firestore()
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    store_data_in_firestore(json_data, 'paystub-entities')

    # Initialize SheetPopulator and populate the Google Sheet
    google_sheets_credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    google_sheets_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing'

    sheet_populator = SheetPopulator(google_sheets_credentials, google_sheets_url)
    general_cell_map = {
        "gross_earnings_ytd": "C30"
        # Add more general entries here
    }
    earnings_cell_map = {
        "Regular": {"rate": "C10", "hours": "G10", "ytd": "C11"},
        "Commission": "C52",
        "Bonus": "C39"  # Combined cell for Bonus and Overtime
    } 
    sheet_populator.populate_sheet(False, json_data, general_cell_map, earnings_cell_map)