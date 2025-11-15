import os
from aws_clients import s3_client
from config import S3_BUCKET_NAME, LOCAL_DATA_DIR
from api_manager import apis

def download_relevant_files(user_prompt, max_files=5):
    """Télécharge les fichiers pertinents depuis S3 selon les mots-clés du prompt."""
    keywords = [w.lower() for w in user_prompt.split() if len(w) > 3]
    english_fallback = {"chine": "china", "énergie": "energy", "loi": "law", "financier": "finance"}
    keywords += [english_fallback.get(k, k) for k in keywords]
    fallback_files = ["reddit", "analysis", "regulation", "directive"]

    apis.set_all_keywords(keywords)

    apis.create_all_files()

    objects = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
    downloaded = 0

    for obj in objects.get("Contents", []):
        key = obj["Key"]
        if key.endswith("/"):
            continue
        if any(kw in key.lower() for kw in keywords + fallback_files):
            local_path = os.path.join(LOCAL_DATA_DIR, key.split("/")[-1])
            if not os.path.exists(local_path):
                s3_client.download_file(S3_BUCKET_NAME, key, local_path)
                print(f"✅ Downloaded: {key}")
                downloaded += 1
            if downloaded >= max_files:
                break

def get_context_from_local_files(user_query, max_files=3):
    """Parcourt le dossier local et retourne le contexte textuel trouvé."""
    snippets, sources = [], []
    keywords = [w.lower() for w in user_query.split() if len(w) > 3]

    for root, _, files in os.walk(LOCAL_DATA_DIR):
        for file in files:
            if file.endswith((".txt", ".html", ".xml", ".csv")):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    if any(kw in text.lower() for kw in keywords):
                        snippets.append(f"[Source: {file}]\n{text[:1500]}")
                        sources.append(file)
                        if len(snippets) >= max_files:
                            return "\n\n".join(snippets), sources
    return "\n\n".join(snippets), sources
