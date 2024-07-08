from .fannie_mae_operations.extraction_scheduleC import scheduleC_extractor
from .fannie_mae_operations.splitter import main_process_batch_splitter
from ..config import get_config
import os
import tempfile

config = get_config(os.getenv('APP_ENV', 'default'))

def process_1040_document(project_id, location, processor_id, pdf_name, file_path, spreadsheet_id):
    tmpdirname = tempfile.mkdtemp()
    
    output_files = main_process_batch_splitter(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        pdf_name=pdf_name,
        file_path=file_path,
        output_files=tmpdirname
    )
    for local_file, _ in output_files:
        
        if 'schedule_C.pdf' in local_file:
            scheduleC_extractor(local_file, spreadsheet_id)