# filter_keywords.py
import json
import re
from pathlib import Path
import boto3, json
from pathlib import Path
# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = Path(__file__).resolve().parent  # Dossier actuel (ex: server/)
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "final_report.json"
OUTPUT_FILE = DATA_DIR / "filtered_report.json"

# --- LISTES DE TERMES ---
BORING_TERMS = {
    "section", "subsection", "paragraph", "plan", "amendment", "act",
    "program", "requirement", "title", "subtitle", "clause", "chapter",
    "authority", "provision", "date", "code", "law", "report", "fund"
}

RELEVANT_TERMS = {
    "energy", "defense", "agriculture", "tax", "funding", "credit", "loan",
    "finance", "market", "spending", "military", "oil", "renewable", "cyber",
    "supply chain", "infrastructure", "budget", "industry", "manufacturing"
}

# --- FONCTION DE NETTOYAGE ---
def clean_terms(terms):
    """Supprime doublons, mots vides, symboles et garde les mots pertinents."""
    cleaned = []
    for t in terms:
        t_lower = t.lower().strip()
        if len(t_lower) < 3 or re.match(r"^\d+$", t_lower):
            continue
        if any(b in t_lower for b in BORING_TERMS):
            continue
        if any(r in t_lower for r in RELEVANT_TERMS):
            cleaned.append(t)
    return sorted(set(cleaned))


# --- Config ---
S3_BUCKET_NAME = "rag-data-pf-2025"
S3_OUTPUT_KEY = "classified/impact_analysis.json"
S3_REGION = "us-west-2"

def upload_to_s3(local_path, bucket, key):
    s3 = boto3.client("s3", region_name=S3_REGION)
    s3.upload_file(str(local_path), bucket, key)
    print(f"✅ Upload réussi : s3://{bucket}/{key}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    input_path = BASE_DIR / "data" / "filtered_report.json"
    output_path = BASE_DIR / "data" / "classified_report.json"

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Exemple de classification ultra simple (à enrichir)
    classified = {
        "summary": data["summary"],
        "impacts": {
            "Defense": "positive",
            "Agriculture": "mixed",
            "Energy": "positive",
            "Food Assistance": "negative"
        },
        "entities": data["entities"]
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(classified, f, indent=2, ensure_ascii=False)

    upload_to_s3(output_path, S3_BUCKET_NAME, S3_OUTPUT_KEY)
