'''from flask import Flask, request, jsonify
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import boto3
import random
import os
import tempfile
import datetime
import re

# --- CONFIGURATION AWS ---
S3_REGION = "us-west-2"
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=S3_REGION
)
s3_client = boto3.client("s3")
aoss_client = boto3.client("opensearchserverless")
bedrock_agent_client = boto3.client("bedrock-agent")

# --- FLASK APP ---
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mo max

# --- VARIABLES ---
s3_bucket_name = "rag-data-pf-2025"
local_data_dir = "./data"
os.makedirs(local_data_dir, exist_ok=True)

print("AWS Region:", S3_REGION)
print("S3 Bucket:", s3_bucket_name)

# --- Vérifie ou crée le bucket ---
try:
    s3_client.head_bucket(Bucket=s3_bucket_name)
    print(f"✅ Bucket '{s3_bucket_name}' already exists.")
except Exception as e:
    print(f"🪣 Creating bucket: {s3_bucket_name}")
    if S3_REGION == "us-west-2":
        s3_client.create_bucket(Bucket=s3_bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=s3_bucket_name,
            CreateBucketConfiguration={'LocationConstraint': S3_REGION}
        )

# --- Lazy Loader : télécharge uniquement les fichiers pertinents ---
def download_relevant_files(user_prompt, bucket, local_dir, max_files=5):
    """
    Télécharge seulement les fichiers dont le nom contient un mot clé du prompt.
    Si aucun mot ne correspond, télécharge quelques fichiers généraux (fallback).
    """
    keywords = [w.lower() for w in user_prompt.split() if len(w) > 3]
    english_fallback = {
        "chine": "china", "énergie": "energy", "régulation": "regulation",
        "marché": "market", "américain": "us", "loi": "law", "financier": "finance"
    }
    keywords += [english_fallback.get(k, k) for k in keywords]

    objects = s3_client.list_objects_v2(Bucket=bucket)
    downloaded = 0
    fallback_files = ["reddit", "x.json", "analysis", "regulation", "act", "directive"]

    for obj in objects.get("Contents", []):
        key = obj["Key"]
        if key.endswith('/'):
            continue

        # Cherche un mot clé ou un fallback dans le nom du fichier
        if any(kw in key.lower() for kw in keywords + fallback_files):
            filename = key.split('/')[-1]
            local_path = os.path.join(local_dir, filename)
            if not os.path.exists(local_path):
                s3_client.download_file(bucket, key, local_path)
                print(f"✅ Téléchargé : {filename}")
                downloaded += 1
            if downloaded >= max_files:
                break

    if downloaded == 0:
        print("⚠️ Aucun fichier correspondant trouvé dans S3. Téléchargement de fichiers de secours...")
        for obj in objects.get("Contents", []):
            if any(f in obj["Key"].lower() for f in fallback_files):
                filename = obj["Key"].split('/')[-1]
                local_path = os.path.join(local_dir, filename)
                if not os.path.exists(local_path):
                    s3_client.download_file(bucket, obj["Key"], local_path)
                    print(f"📦 Fichier par défaut téléchargé : {filename}")
                    downloaded += 1
                if downloaded >= 3:
                    break


# --- CONTEXTE LOCAL (RAG) ---
def get_context_from_local_files(user_query, max_files=3):
    """
    Parcourt ./data pour trouver les fichiers contenant des mots du prompt utilisateur.
    Retourne le texte extrait et la liste des sources utilisées.
    """
    local_dir = "./data"
    context_snippets = []
    matched_files = []

    keywords = [w.lower() for w in user_query.split() if len(w) > 3]

    for root, _, files in os.walk(local_dir):
        for file in files:
            if file.endswith((".txt", ".html", ".xml", ".csv")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                        if any(kw in text.lower() for kw in keywords):
                            snippet = text[:1500]
                            # ✅ Ajout de la provenance réelle
                            context_snippets.append(f"[Source: {file}]\n{snippet}")
                            matched_files.append(file)
                            print(f"✅ Fichier pertinent trouvé : {file}")
                            if len(context_snippets) >= max_files:
                                break
                except Exception as e:
                    print(f"⚠️ Erreur lecture {file}: {e}")
                    continue

    if not matched_files:
        print("❌ Aucun contexte pertinent trouvé.")
    return "\n\n".join(context_snippets), matched_files

def upload_to_bucket(file_content, file_extension):
    if file_content:
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            file_key = f"uploads/{timestamp}.{file_extension or 'txt'}"

            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension or 'txt'}") as tmp:
                tmp.write(file_content.encode("utf-8"))
                tmp_path = tmp.name

            s3_client.upload_file(tmp_path, s3_bucket_name, file_key)
            os.remove(tmp_path)

            s3_url = f"s3://{s3_bucket_name}/{file_key}"
            print(f"✅ Fichier uploadé : {s3_url}")
        except Exception as e:
            return jsonify({"response": f"[Erreur S3] {e}"}), 500
        
# --- ROUTE CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    """Reçoit le prompt utilisateur et appelle le modèle Bedrock."""
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"response": f"[Erreur JSON] {e}"}), 413

    user_prompt = data.get("prompt", "")
    file_content = data.get("file_content")
    file_extension = data.get("file_extension")

    s3_url = None

    # --- Étape 1 : upload d’un éventuel fichier utilisateur ---
    upload_to_bucket(file_content=file_content, file_extension=file_extension)

    # --- Étape 2 : Lazy loading & RAG ---
    download_relevant_files(user_prompt, s3_bucket_name, local_data_dir)
    context_text, sources = get_context_from_local_files(user_prompt)

    if context_text:
        llm_prompt = (
            f"Relevant context extracted from S3 documents:\n{context_text}\n\n"
            f"User question: {user_prompt}\n\n"
            f"Available S3 sources: {sources}"
        )
        print("📚 Contexte enrichi ajouté au prompt.")
    else:
        llm_prompt = user_prompt
        print("⚠️ Aucun contexte ajouté.")

    # --- Étape 3 : Appel Bedrock ---
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

    system_prompt = (
"You are 'Regulus v3', a Regulatory & Market Intelligence Co-Pilot for financial analysis teams.\n\n"

"MISSION\n"
"Analyze regulatory, financial, and social data to extract decision-ready insights for S&P 500 portfolio management.\n"
"You are allowed to use ONLY the content explicitly provided in the user input or S3-referenced documents.\n"
"If no evidence is given, respond with placeholders and state clearly that data is missing.\n\n"

"---\n\n"
"🎯 OBJECTIVE\n"
"Generate concise, source-grounded, and interpretable insights about:\n"
"- Regulatory developments and their financial implications,\n"
"- Sectoral risk and opportunity analysis,\n"
"- Market sentiment shifts,\n"
"- Comparative views between jurisdictions (EU, US, CN).\n\n"

"---\n\n"
"⚙️ INPUT CONTEXT\n"
"You may receive text excerpts from:\n"
"- Regulatory texts (laws, directives, acts),\n"
"- Financial filings (10-K, ESG reports),\n"
"- Market commentary (Reddit, X),\n"
"- News articles or press releases.\n\n"
"If the user does NOT provide any of these sources, you MUST NOT infer or invent any facts.\n"
"Instead, write: 'No data provided — additional source required.'\n\n"

"---\n\n"
"📊 STRICT OUTPUT FORMAT (JSON only)\n"
"{\n"
'  "summary": "Brief synthesis (2-3 sentences, or \'No data provided.\')",\n'
'  "entities": {\n'
'    "companies": ["..."],\n'
'    "sectors": ["..."],\n'
'    "countries": ["..."]\n'
"  },\n"
'  "jurisdictions": ["EU","US","CN","JP", "..."],\n'
'  "regulation_details": {\n'
'    "law_name": "string or null",\n'
'    "type": "string (\'tax\', \'subsidy\', \'restriction\', \'disclosure\', etc.)",\n'
'    "application_date": "YYYY-MM-DD or null",\n'
'    "description": "short summary or \'No data.\'"\n'
"  },\n"
'  "regulatory_risk": {\n'
'    "score": 0.0-1.0,\n'
'    "drivers": ["top 3 factors raising the risk"],\n'
'    "mitigations": ["top 3 mitigating elements"]\n'
"  },\n"
'  "market_mood": {\n'
'    "reddit": {"score": -1..1, "n": int},\n'
'    "x": {"score": -1..1, "n": int},\n'
'    "blend": -1..1,\n'
'    "interpretation": "1-2 sentences summarizing overall market tone or \'No data.\'"\n'
"  },\n"
'  "comparative_view": {\n'
'    "dimension": "compliance_cost | incentives | data_obligations | carbon",\n'
'    "EU_vs_US": "contrast or \'No data.\'",\n'
'    "EU_vs_CN": "contrast or \'No data.\'",\n'
'    "US_vs_CN": "contrast or \'No data.\'"\n'
"  },\n"
'  "impact_estimation": {\n'
'    "magnitude": -1.0..1.0,\n'
'    "confidence": 0.0..1.0\n'
"  },\n"
'  "recommendations": ["Actionable suggestions or \'Not enough evidence.\'"],\n'
'  "sources": [\n'
'    {"s3_key": "bucket/key", "snippet": "<=200 chars explaining relevance"}\n'
"  ]\n"
"}\n\n"

"---\n\n"
"🔒 CONSTRAINTS\n"
"- Do NOT hallucinate. Use only facts supported by explicit input or S3 content.\n"
"- If no evidence exists, return neutral placeholders ('null', 'No data', '0.0', etc.).\n"
"- Each cited file in 'sources' MUST correspond to a real provided key.\n"
"- Never generate imaginary S3 keys or external URLs.\n"
"- Keep tone professional, factual, and investment-oriented.\n\n"

"---\n\n"
"💡 STYLE GUIDELINES\n"
"- Short declarative sentences.\n"
"- Quantify wherever possible.\n"
"- Explain causal links ('due to tax reform', 'driven by subsidy incentives').\n"
"- Output must be clean, valid JSON, parsable without post-processing.\n"
)


    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": llm_prompt}]}
        ]
    }

    try:
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload)
        )
        result = json.loads(response["body"].read())
        generated_text = "".join(
            [part["text"] for part in result.get("content", []) if "text" in part]
        )
        return jsonify({"response": generated_text, "s3_url": s3_url, "sources": sources}), 200

    except Exception as e:
        print(f"❌ Erreur Bedrock: {e}")
        return jsonify({"response": f"[Erreur Bedrock] {e}"}), 500


if __name__ == "__main__":
    #app.run(debug=True, use_reloader=False)
    app.run(debug=True)'''

