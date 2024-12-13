from google.cloud import storage
from werkzeug.datastructures import FileStorage
from app.utils.config import Config

def upload_to_bucket(bucket_name, file):
    if not bucket_name:
        raise ValueError("Cannot determine path without bucket name.")  
    
    storage_client = storage.Client.from_service_account_json(Config.SERVICE_ACCOUNT_FILE)
    
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(file.filename)  
    blob.upload_from_file(file)  
    return blob.public_url  