from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

print("Creating Flask app...")
app_env = os.environ.get('APP_ENV', 'production')
application = create_app(app_env)
print(f"Flask app created with environment: {app_env}")

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() in ['true', '1', 't']
    print(f"Running Flask app in debug mode: {debug_mode}")
    application.run(debug=debug_mode, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
