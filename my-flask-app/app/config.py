import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False

    # Google Cloud configurations
    PROJECT_ID = os.getenv('GCP_PROJECT_ID')
    LOCATION = os.getenv('GCP_LOCATION')

    # Document AI processor IDs
    PAYSTUB_PROCESSOR_ID = os.getenv('PAYSTUB_PROCESSOR_ID')
    W2_PROCESSOR_ID = os.getenv('W2_PROCESSOR_ID')
    SPLITTER_PROCESSOR_ID = os.getenv('SPLITTER_PROCESSOR_ID')
    

    # Google Cloud Storage configurations
    GCS_BUCKET = os.getenv('GCS_BUCKET_NAME')
    INPUT_BUCKET = os.getenv('GCS_INPUT_BUCKET')
    OUTPUT_BUCKET = os.getenv('GCS_OUTPUT_BUCKET')

    INPUT_URI = os.getenv('GCS_INPUT_URI')
    OUTPUT_URI = os.getenv('GCS_OUTPUT_URI')

    # Google Sheets API configuration
    GOOGLE_SHEETS_URL_INCOME_ANALYSER = os.getenv('GOOGLE_SHEETS_URL_INCOME_ANALYSER')
    GOOGLE_SHEETS_URL_FANNIE_MAE = os.getenv('GOOGLE_SHEETS_URL_FANNIE_MAE')

    # Credentials Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_STORAGE_CREDENTIALS = os.getenv('GOOGLE_STORAGE_CREDENTIALS')
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    GOOGLE_FIRESTORE_CREDENTIALS = os.getenv('GOOGLE_FIRESTORE_CREDENTIALS')

    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    SECRET_KEY = 'development_secret_key'  # Consider using a more secure approach for production

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'testing_secret_key'  # Consider using a more secure approach for production

class ProductionConfig(Config):
    APP_ENV = 'production'

# Dictionary to help select the right configuration based on the environment
config_by_name = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Default to development if unspecified
}

def get_config(env):
    if env == 'development':
        return DevelopmentConfig()
    elif env == 'testing':
        return TestingConfig()
    elif env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()
