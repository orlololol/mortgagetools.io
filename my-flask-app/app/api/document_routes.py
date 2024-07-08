from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.services.document_processing_w2_paystub import process_document_w2_paystub
from app.services.document_processing_fannie_mae import process_document_fannie_mae
import os

# Define allowed extensions
ALLOWED_EXTENSIONS = {'pdf'}

api_blueprint = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_blueprint.route('/process', methods=['POST'])
def process_documents():
    document_type = request.form.get('document_type')
    spreadsheet_id = request.form.get('spreadsheetId')

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        try:
            if document_type in ['paystub', 'w2']:
                process_document_w2_paystub(file_path, 'application/pdf', document_type, spreadsheet_id)
            elif document_type == '1040':
                process_document_fannie_mae(file_path, document_type, file.filename, spreadsheet_id)
            else:
                return jsonify({'error': 'Invalid document type'}), 400
        finally:
            # Ensure the file is deleted after processing
            if os.path.exists(file_path):
                os.remove(file_path)

        return jsonify({'message': 'Document processed successfully'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200
