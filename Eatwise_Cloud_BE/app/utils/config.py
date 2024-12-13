import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "34.101.149.230")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "eatwise-sql")
    DB_NAME = os.getenv("DB_NAME", "eatwise-db-data")
    BUCKET_NAME = os.getenv("BUCKET_NAME", "eatwise-bucket-1")
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "./service-account.json")
