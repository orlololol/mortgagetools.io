from google.cloud import documentai_v1 as documentai

def online_process(project_id, location, processor_id, file_path, mime_type):
    opts = {"api_endpoint": f"{location}-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    resource_name = client.processor_path(project_id, location, processor_id)
    with open(file_path, "rb") as file:
        file_content = file.read()
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)
    return client.process_document(request=request)
