import firebase_admin
from firebase_admin import credentials, firestore
from ..config import get_config
import os
import json
import base64

config = get_config(os.getenv('APP_ENV', 'default'))


def initialize_firestore():
    service_account_path = os.getenv('GOOGLE_FIRESTORE_CREDENTIALS')
    cred = credentials.Certificate(service_account_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    else:
        print("Firebase app already initialized.")

def store_data_in_firestore(data, collection_name):
    db = firestore.client()
    doc_ref = db.collection(collection_name).document()
    doc_ref.set({"entities": data})
