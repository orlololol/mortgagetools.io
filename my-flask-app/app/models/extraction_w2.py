from typing import List, Dict, Any
from google.cloud import documentai_v1 as documentai
from ..utils.doc_ai_util import online_process
from ..utils.firestore_util import initialize_firestore, store_data_in_firestore
from ..utils.google_sheets_util import SheetPopulator
import json
from ..config import get_config
import os

# Get the current environment ('development', 'testing', 'production')
env = os.getenv('APP_ENV', 'default')

# Get the configuration for the current environment
config = get_config(env)

def save_data_to_json(data, filename='data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    return filename

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

def w2_extractor(project_id, location, processor_id, file_path, mime_type, spreadsheet_id):
    document = online_process(project_id, location, processor_id, file_path, mime_type)
    data = extract_data(document.document)
    
    json_filename = save_data_to_json(data)
    initialize_firestore()
    store_data_in_firestore(data, 'w2-entities')

    # Initialize SheetPopulator and populate the Google Sheet
    google_sheets_credentials = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    google_sheets_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?usp=sharing'
    
    sheet_populator = SheetPopulator(google_sheets_credentials, google_sheets_url)

    sheet_populator.populate_sheet(True, data)