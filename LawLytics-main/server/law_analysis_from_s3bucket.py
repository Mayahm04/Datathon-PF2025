# law_analysis_pipeline.py
import boto3
import json
from preprocess_utils import preprocess_with_comprehend
from summarize_law_texts_bedrock import summarize_with_bedrock

# --- CONFIGURATION S3 ---
S3_BUCKET_NAME = "textlaw"  # ton bucket existant
S3_KEY = "2.H.R.1 - One Big Beautiful Bill Act.xml"  # chemin dans ton bucket
S3_REGION = "us-west-2"

def read_file_from_s3(bucket_name, key):
    """Télécharge un fichier texte depuis S3 et retourne son contenu."""
    s3_client = boto3.client("s3", region_name=S3_REGION)
    print(f"📥 Téléchargement du fichier depuis S3 : s3://{bucket_name}/{key}")
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        text = obj["Body"].read().decode("utf-8")
    except UnicodeDecodeError:
        obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        text = obj["Body"].read().decode("latin-1", errors="ignore")
    return text

if __name__ == "__main__":
    print("⚙️ Lancement du pipeline complet (Comprehend + Bedrock)...")

    # 1️⃣ Lecture du texte source depuis S3
    text = read_file_from_s3(S3_BUCKET_NAME, S3_KEY)

    # 2️⃣ Extraction sémantique via Comprehend
    results, s3_path = preprocess_with_comprehend(text)
    print(f"✅ {len(results['entities'])} entités et {len(results['key_phrases'])} phrases clés détectées.")
    print(f"📤 Résultats uploadés sur : {s3_path}")

    # 3️⃣ Résumé analytique via Bedrock
    summary = summarize_with_bedrock(text)
    print("\n🧾 Résumé final :\n")
    print(summary)

    # 4️⃣ Sauvegarde du rapport combiné
    report = {
        "entities": results["entities"],
        "key_phrases": results["key_phrases"],
        "summary": summary
    }

    with open("data/final_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n📦 Rapport complet enregistré sous data/final_report.json")
