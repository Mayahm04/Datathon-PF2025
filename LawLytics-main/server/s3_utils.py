import os, tempfile, datetime
from aws_clients import s3_client
from config import S3_BUCKET_NAME

def ensure_bucket_exists():
    """Vérifie ou crée le bucket S3."""
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"✅ Bucket '{S3_BUCKET_NAME}' already exists.")
    except Exception:
        print(f"🪣 Creating bucket: {S3_BUCKET_NAME}")
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)

def upload_to_bucket(file_content, file_extension="txt"):
    """Upload un fichier utilisateur vers S3."""
    if not file_content:
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_key = f"uploads/{timestamp}.{file_extension}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
        tmp.write(file_content.encode("utf-8"))
        tmp_path = tmp.name

    s3_client.upload_file(tmp_path, S3_BUCKET_NAME, file_key)
    os.remove(tmp_path)
    s3_url = f"s3://{S3_BUCKET_NAME}/{file_key}"
    print(f"✅ Uploaded: {s3_url}")
    return s3_url
