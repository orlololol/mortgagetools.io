from flask import current_app as app
import os
from ..utils.doc_ai_util import online_process
from ..models.extraction_paystub import paystub_extractor as extract_paystub
from ..models.extraction_w2 import w2_extractor as extract_w2
from app.config import get_config

# Get the configuration for the current environment
config = get_config(os.getenv('APP_ENV', 'default'))

def process_document_w2_paystub(file_path, mime_type, document_type, spreadsheet_id):
    """
    Process a document based on the document type using configurations from the Flask app.
    
    :param file_path: Path to the file to be processed
    :param mime_type: MIME type of the file
    :param document_type: Type of the document (e.g., 'paystub', 'w2')
    :return: Result of the processing
    """
    # Retrieve configuration from Flask app context
    project_id = config.PROJECT_ID
    location = config.LOCATION
    if document_type == 'paystub':
        processor_id = config.PAYSTUB_PROCESSOR_ID 
    elif document_type == 'w2': 
        processor_id = config.W2_PROCESSOR_ID

    # Call the appropriate extractor based on document type
    if document_type == 'paystub':
        return extract_paystub(project_id, location, processor_id, file_path, mime_type, spreadsheet_id)
    elif document_type == 'w2':
        return extract_w2(project_id, location, processor_id, file_path, mime_type, spreadsheet_id)
    else:
        raise ValueError(f"Unsupported document type: {document_type}")