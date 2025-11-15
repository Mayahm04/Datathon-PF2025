import os

# --- CONFIGURATION AWS ---
S3_REGION = "us-west-2"
S3_BUCKET_NAME = "rag-data-pf-2025"
LOCAL_DATA_DIR = "./data"
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
