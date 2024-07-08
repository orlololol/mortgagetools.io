import os
from google.cloud import storage
from google.oauth2 import service_account
from ..config import get_config

config = get_config(os.getenv('APP_ENV', 'default'))

def initialize_gcs_client():
    credentials = service_account.Credentials.from_service_account_file(os.getenv('GOOGLE_STORAGE_CREDENTIALS'))
    client = storage.Client(credentials=credentials, project=config.PROJECT_ID)
    return client

def download_blob(storage_client, bucket_name, blob_name, destination_file_name):
    """Downloads a blob from the specified GCS bucket."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    try:
        blob.download_to_filename(destination_file_name)
        print(f"Blob {blob_name} downloaded to {destination_file_name}.")
    except Exception as e:
        print(f"Failed to download {blob_name}: {e}")

def upload_file_to_gcs(file_path, bucket_name, blob_path):
    """Uploads a single file to a specific GCS directory."""
    client = initialize_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(file_path)
    print(f"Uploaded {file_path} to gs://{bucket_name}/{blob_path}")
