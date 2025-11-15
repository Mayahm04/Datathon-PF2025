import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from prompts.systeme_prompt import system_prompt
from finance_utils import get_stock_data

from s3_utils import ensure_bucket_exists, upload_to_bucket
from rag_utils import download_relevant_files, get_context_from_local_files
from bedrock_utils import call_bedrock
from config import S3_BUCKET_NAME
import json
import re

app = Flask(__name__)
CORS(app)

ensure_bucket_exists()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    file_content = data.get("file_content")
    file_extension = data.get("file_extension", "txt")

    s3_url = upload_to_bucket(file_content, file_extension)

    # --- Étape 1 : Récupération du contexte réglementaire ---
    download_relevant_files(user_prompt)
    context_text, sources = get_context_from_local_files(user_prompt)

    # --- Étape 2 : Données financières dynamiques ---
    finance_context = ""
    ticker_map = {
        "apple": "AAPL",
        "tesla": "TSLA",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "sinopec": "SNP",
        "total": "TTE",
        "google": "GOOGL",
        "meta": "META"
    }

    for name, ticker in ticker_map.items():
        if name in user_prompt.lower():
            finance_context = get_stock_data(ticker , with_projection=True)
            break

    # --- Étape 3 : Construction du prompt final pour le LLM ---
    if context_text:
        llm_prompt = (
            f"Relevant context extracted from S3 documents:\n{context_text}\n\n"
            f"User question:\n{user_prompt}\n\n"
            f"📊 Financial market data (from Yahoo Finance):\n{finance_context or 'No financial data found.'}\n\n"
            f"Available S3 sources:\n{sources}"
        )
    else:
        llm_prompt = (
            f"User question:\n{user_prompt}\n\n"
            f"📊 Financial data:\n{finance_context or 'No financial data found.'}"
        )

    # --- Étape 4 : Appel du modèle Bedrock ---
    generated_text = call_bedrock(system_prompt, llm_prompt)

    cleaned_text = extract_json(generated_text)
    try:
        res = json.loads(cleaned_text)
    except Exception as e:
        print(f"⚠️ Not valid JSON output: {e}")
        print("Generated text was:", cleaned_text)
        res = {"raw_text": cleaned_text}

    return jsonify({
    "summary": res.get("summary", ""),
    "sectors": res.get("sectors", []),
    "stocks": res.get("stocks", []),
    "recommendations": res.get("recommendations", []),
    "sources": res.get("sources", []),
    "s3_url": s3_url
    })


from preprocess_utils import preprocess_and_upload
import tempfile, os

@app.route("/preprocess_law", methods=["POST"])
def preprocess_law():
    """
    Endpoint flexible :
    - Si on envoie un file_path → traite un fichier local.
    - Si on envoie file_content → sauvegarde temporairement, traite, puis supprime.
    """
    data = request.get_json()

    # --- Cas 1 : fichier local ---
    xml_path = data.get("file_path")
    if xml_path and os.path.exists(xml_path):
        s3_key = preprocess_and_upload(xml_path)
        return jsonify({
            "message": "✅ Law preprocessed and uploaded (local file).",
            "s3_key": s3_key
        })

    # --- Cas 2 : fichier envoyé depuis le frontend ---
    file_content = data.get("file_content")
    file_extension = data.get("file_extension", "xml")

    if file_content:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
            tmp.write(file_content.encode("utf-8"))
            tmp_path = tmp.name

        s3_key = preprocess_and_upload(tmp_path)
        os.remove(tmp_path)

        return jsonify({
            "message": "✅ Law preprocessed and uploaded (uploaded file).",
            "s3_key": s3_key
        })

    return jsonify({"error": "Missing file_path or file_content in request."}), 400

def extract_json(text: str):
    """Remove code fences and safely extract JSON from LLM output."""
    # Remove code block markers
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = text.strip("`").strip()
    # Extract JSON block if any
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text

if __name__ == "__main__":
    app.run(debug=True)
