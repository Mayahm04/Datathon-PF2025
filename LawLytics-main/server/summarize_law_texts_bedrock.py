# summarize_bedrock.py
import boto3, json

# --- Config AWS Bedrock ---
bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")

def summarize_with_bedrock(text):
    """
    Résume la loi en 10 points clairs (impact économique, fiscal, énergétique, etc.)
    """
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2500,
        "temperature": 0.4,
        "system": "You are an expert in financial and legislative analysis.",
        "response_format": {"type": "json"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
Summarize the following U.S. legislative text in 10 concise bullet points.
Focus on its economic, energy, defense, and fiscal policy impacts.
Use plain English and be specific when possible.

Legislative text:
{text[:12000]}
"""
                    }
                ]
            }
        ]
    }

    response = bedrock.invoke_model(
        modelId="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps(payload)
    )

    result = json.loads(response["body"].read())
    summary = "".join([p["text"] for p in result["content"] if "text" in p])
    return summary


if __name__ == "__main__":
    # 🔹 Lis ton fichier de loi (avec fallback d'encodage)
    try:
        with open("data/2.H.R.1 - One Big Beautiful Bill Act.xml", "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open("data/2.H.R.1 - One Big Beautiful Bill Act.xml", "r", encoding="latin-1", errors="ignore") as f:
            text = f.read()

    print("⏳ Résumé en cours avec Claude Sonnet...")
    summary = summarize_with_bedrock(text)

    print("\n✅ Résumé généré :\n")
    print(summary)
