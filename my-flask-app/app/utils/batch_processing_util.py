import os
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
from google.cloud.documentai_toolbox import document
from ..config import get_config

config = get_config(os.getenv('APP_ENV', 'default'))


def setup_documentai_processing_batch(project_id, location, processor_id, pdf_name, mime_type="application/pdf"):
    input_uri=config.INPUT_URI+pdf_name
    output_uri=config.OUTPUT_URI
    print(f"Input URI: {input_uri}")
    print(f"Output URI: {output_uri}")
    print(f"Project ID: {project_id}")
    print(f"Location: {location}")
    print(f"Processor ID: {processor_id}")
    
    
    client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    )
    # Create a GcsDocument for a single document processing
    gcs_document = documentai.GcsDocument(
        gcs_uri=input_uri,
        mime_type=mime_type
    )
    gcs_documents = documentai.GcsDocuments(documents=[gcs_document])
    input_config = documentai.BatchDocumentsInputConfig(gcs_documents=gcs_documents)

    output_config = documentai.DocumentOutputConfig(
        gcs_output_config=documentai.DocumentOutputConfig.GcsOutputConfig(gcs_uri=output_uri)
    )

    request = documentai.BatchProcessRequest(
        name=client.processor_path(project_id, location, processor_id),
        input_documents=input_config,
        document_output_config=output_config
    )

    operation = client.batch_process_documents(request)
    print("Batch processing started for a single document...")
    operation.result(timeout=900)  # Wait up to 15 minutes
    print("Document processing completed.")
    return operation

def get_output_paths(operation):
    from google.cloud.documentai_v1 import BatchProcessMetadata
    metadata = BatchProcessMetadata(operation.metadata)
    output_paths = []
    for process_status in metadata.individual_process_statuses:
        if process_status.status.code == 0:
            output_gcs_destination = process_status.output_gcs_destination
            if not output_gcs_destination.endswith('/'):
                output_gcs_destination += '/'
            output_paths.append(output_gcs_destination)
    return output_paths

def split_pdf_from_json(document_path, pdf_path, output_folder):
    wrapped_document = document.Document.from_document_path(document_path=document_path)
    output_files = wrapped_document.split_pdf(pdf_path=pdf_path, output_path=output_folder)
    
    print("Document Successfully Split")
    for output_file in output_files:
        print(output_file)