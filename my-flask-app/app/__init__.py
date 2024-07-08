import os
import json
import tempfile
from flask import Flask
from flask_cors import CORS

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(f'app.config.{config_name.capitalize()}Config')

    # Decode the JSON credentials from environment variables
    credentials_env_vars = [
        'GOOGLE_APPLICATION_CREDENTIALS',
        'GOOGLE_STORAGE_CREDENTIALS',
        'GOOGLE_SHEETS_CREDENTIALS',
        'GOOGLE_FIRESTORE_CREDENTIALS'
    ]

    for env_var in credentials_env_vars:
        json_credentials = os.getenv(env_var)

        if json_credentials:
            # Check if the credentials string ends with .json
            if not json_credentials.endswith('.json'):
                try:
                    credentials_data = json.loads(json_credentials)
                except json.JSONDecodeError:
                    raise RuntimeError(f"Error decoding JSON for {env_var}")

                # Create a temporary file to store the credentials
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
                    json.dump(credentials_data, f)
                    temp_credentials_path = f.name

                # Set the environment variable to point to the temporary file
                os.environ[env_var] = temp_credentials_path
            else:
                # If it already ends with .json, set the path environment variable directly
                os.environ[env_var] = json_credentials
        else:
            raise RuntimeError(f"The {env_var} environment variable is not set.")

    # Register blueprints
    from .api.document_routes import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    CORS(app)

    return app
