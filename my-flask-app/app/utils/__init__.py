import secrets
secret_key = secrets.token_urlsafe(32)  # Generates a 32-byte (256-bit) URL-safe secret key
print(secret_key)