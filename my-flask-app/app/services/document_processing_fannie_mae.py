from flask import current_app as app
import os
from ..models.fannie_mae_1040_extraction import process_1040_document
from app.config import get_config

# Get the configuration for the current environment
config = get_config(os.getenv('APP_ENV', 'default'))

def process_document_fannie_mae(file_path, document_type, pdf_name, spreadsheet_id):
    """
    Process a document based on the document type using configurations from the Flask app.
    
    :param file_path: Path to the file to be processed
    :param pdf_name:  Name of the pdf file
    :param document_type: Type of the document (e.g., 'paystub', 'w2', '1040')
    """
    # Retrieve configuration from Flask app context
    project_id = config.PROJECT_ID
    location = config.LOCATION
    if document_type == '1040':
        processor_id = config.SPLITTER_PROCESSOR_ID 
        process_1040_document(project_id, location, processor_id, pdf_name, file_path, spreadsheet_id=spreadsheet_id)
    