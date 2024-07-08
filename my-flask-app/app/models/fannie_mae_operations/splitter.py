import os
from google.cloud import storage
from ...utils.gcs_operations import download_blob, upload_file_to_gcs
from ...utils.batch_processing_util import setup_documentai_processing_batch, get_output_paths, split_pdf_from_json
from ...config import get_config


# Get the current environment ('development', 'testing', 'production')
env = os.getenv('APP_ENV', 'default')

# Get the configuration for the current environment
config = get_config(env)

def main_process_batch_splitter(project_id, location, processor_id, pdf_name, file_path, output_files):

    processing_dir = os.path.dirname(file_path)
    upload_file_to_gcs(file_path, config.INPUT_BUCKET, pdf_name)

    operation = setup_documentai_processing_batch(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        pdf_name=pdf_name,
    )
    # Find the JSON output file
    storage_client = storage.Client(project_id)

    output_directories = get_output_paths(operation)
    print("json_path:", output_directories)
    
    tmpdirname = output_files
    local_json_path = os.path.join(tmpdirname, 'output-document.json')
    local_pdf_path = os.path.join(tmpdirname, pdf_name) 
    
    for directory in output_directories:
        json_file_path = directory + "output-document.json"
        bucket_name, blob_path = directory.replace('gs://', '').split('/', 1)
        # Download the JSON
        download_blob(storage_client, bucket_name, blob_path + "output-document.json", local_json_path)
    
    # Download the original PDF from the correct bucket
    try:
        download_blob(storage_client, config.INPUT_BUCKET, pdf_name, local_pdf_path) 
    except Exception as e:
        print(f"Error downloading original PDF: {e}")
        return  # Exit if PDF can't be downloaded

    # Split PDF into smaller PDFs in the temporary directory
    try:
        split_pdf_from_json(local_json_path, local_pdf_path, tmpdirname)
    except Exception as e:
        print(f"Error splitting PDF: {e}")
        return

    print(f"Split PDFs to {tmpdirname}")
    print(f"input file path: {processing_dir}")
    file_paths = []  # List to store local file paths
    # Save the local path of each split file along with its GCS path
    for file in os.listdir(tmpdirname):
        local_file_path = os.path.join(tmpdirname, file)
        gcs_file_path = f"gs://{config.OUTPUT_BUCKET}/{blob_path}split_pdfs/{file}"
        file_paths.append((local_file_path, gcs_file_path))

    # Upload the split PDFs
    for local_file_path, gcs_file_path in file_paths:
        bucket_name, blob_path = gcs_file_path.replace('gs://', '').split('/', 1)
        upload_file_to_gcs(local_file_path, bucket_name, blob_path)

    print("All operations completed successfully.")

    return file_paths  # Return list of tuples containing local and GCS file paths