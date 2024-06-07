from flask import Flask, request, jsonify
from flask_cors import CORS  # Ensure this is imported

app = Flask(__name__)
CORS(app)  # This should apply CORS to all routes and origins

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        return jsonify({'message': 'File uploaded successfully', 'filename': file.filename}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
