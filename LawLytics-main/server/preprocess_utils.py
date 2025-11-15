# preprocess_utils.py
import boto3
import re
import json
from bs4 import BeautifulSoup
from aws_clients import bedrock_client, s3_client
from config import S3_BUCKET_NAME
import os
import tempfile
import chardet  

def extract_clean_text_from_xml(xml_path):
    """Nettoie un texte XML (comme une loi USLM) et extrait les sections."""
    # --- Lire le fichier avec détection automatique d'encodage ---
    with open(xml_path, "rb") as f:
        raw_data = f.read()

    # Essayer de détecter l'encodage (grâce à chardet)
    detected = chardet.detect(raw_data)
    encoding = detected["encoding"] or "utf-8"

    try:
        content = raw_data.decode(encoding)
    except UnicodeDecodeError:
        print(f"⚠️ Erreur de décodage avec {encoding}, tentative avec latin-1")
        content = raw_data.decode("latin-1", errors="ignore")

    soup = BeautifulSoup(content, "xml")
    sections = soup.find_all("section")

    cleaned_sections = []
    for s in sections:
        section_id = s.get("id", "")
        title = s.find("heading")
        title = title.text if title else "Untitled"
        text = re.sub(r"\s+", " ", s.get_text())
        cleaned_sections.append({
            "id": section_id,
            "title": title.strip(),
            "text": text.strip()[:20000]
        })

    return cleaned_sections



def enrich_with_comprehend(section_text, language="en"):
    """Analyse NLP via Amazon Comprehend : entités, key phrases, sentiment."""
    comprehend = boto3.client('comprehend', region_name='us-west-2')

    entities = comprehend.detect_entities(Text=section_text[:5000], LanguageCode=language)
    key_phrases = comprehend.detect_key_phrases(Text=section_text[:5000], LanguageCode=language)

    return {
        "entities": [e["Text"] for e in entities["Entities"]],
        "key_phrases": [k["Text"] for k in key_phrases["KeyPhrases"]]
    }


def summarize_with_bedrock(section_text, title):
    """Résumé contextuel via Claude 3 Sonnet (Bedrock format 2024+)."""
    prompt = (
        f"Summarize the following law section focusing on its economic, financial, and environmental implications.\n\n"
        f"Title: {title}\n\n"
        f"Text:\n{section_text[:5000]}"
    )

    body = {
        "anthropic_version": "bedrock-2023-05-31",  # obligatoire
        "max_tokens": 500,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    try:
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(body)
        )

        result = json.loads(response["body"].read())

        if "content" in result and len(result["content"]) > 0:
            return result["content"][0]["text"]
        else:
            return "⚠️ No summary returned from model."
    except Exception as e:
        print(f"❌ Bedrock error in section '{title}': {e}")
        return "⚠️ Summary unavailable (Bedrock error)"


'''def preprocess_and_upload(xml_path):
    """Pipeline complet : extraction, enrichissement, upload S3."""
    sections = extract_clean_text_from_xml(xml_path)

    all_processed = []
    for s in sections:
        enrich = enrich_with_comprehend(s["text"])
        summary = summarize_with_bedrock(s["text"], s["title"])

        item = {
            "title": s["title"],
            "summary": summary,
            "entities": enrich["entities"],
            "key_phrases": enrich["key_phrases"]
        }
        all_processed.append(item)

    # Sauvegarde temporaire + upload vers S3
    file_name = os.path.basename(xml_path).replace(".xml", "_summary.json")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json.dump(all_processed, tmp, indent=2)
        tmp_path = tmp.name

    s3_key = f"preprocessed/{file_name}"
    s3_client.upload_file(tmp_path, S3_BUCKET_NAME, s3_key)
    os.remove(tmp_path)

    print(f"✅ Uploaded summarized law to S3://{S3_BUCKET_NAME}/{s3_key}")
    return s3_key'''

def preprocess_and_upload(xml_path):
    """Pipeline complet : extraction, enrichissement, upload S3."""
    sections = extract_clean_text_from_xml(xml_path)
    all_processed = []

    total = len(sections)
    print(f"🧾 {total} sections trouvées. Début du traitement...\n")

    for i, s in enumerate(sections, start=1):
        print(f"➡️  Section {i}/{total} : {s['title'][:60]}...")

        try:
            enrich = enrich_with_comprehend(s["text"])
        except Exception as e:
            print(f"❌ Comprehend error in section '{s['title']}': {e}")
            enrich = {"entities": [], "key_phrases": []}

        try:
            summary = summarize_with_bedrock(s["text"], s["title"])
        except Exception as e:
            print(f"❌ Bedrock error in section '{s['title']}': {e}")
            summary = "Error during summary generation."

        all_processed.append({
            "title": s["title"],
            "summary": summary,
            "entities": enrich["entities"],
            "key_phrases": enrich["key_phrases"]
        })

    print("\n📤 Upload du résultat sur S3...")
    file_name = os.path.basename(xml_path).replace(".xml", "_summary.json")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json.dump(all_processed, tmp, indent=2)
        tmp_path = tmp.name

    s3_key = f"preprocessed/{file_name}"
    s3_client.upload_file(tmp_path, S3_BUCKET_NAME, s3_key)
    os.remove(tmp_path)

    print(f"✅ Fichier final : S3://{S3_BUCKET_NAME}/{s3_key}")
    return s3_key


    # Sauvegarde temporaire + upload vers S3
    file_name = os.path.basename(xml_path).replace(".xml", "_summary.json")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        json.dump(all_processed, tmp, indent=2)
        tmp_path = tmp.name

    s3_key = f"preprocessed/{file_name}"
    s3_client.upload_file(tmp_path, S3_BUCKET_NAME, s3_key)
    #os.remove(tmp_path)

    print(f"✅ Uploaded summarized law to S3://{S3_BUCKET_NAME}/{s3_key}")
    return s3_key

