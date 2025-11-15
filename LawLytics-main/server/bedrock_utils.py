import json
from aws_clients import bedrock_client

def call_bedrock(system_prompt, llm_prompt):
    """Appelle le modèle Claude 3 Sonnet sur Bedrock."""
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.5,
        "system": system_prompt,
        "messages": [{"role": "user", "content": [{"type": "text", "text": llm_prompt}]}]
    }

    response = bedrock_client.invoke_model(
        #modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        modelId = "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        body=json.dumps(payload)
    )
    result = json.loads(response["body"].read())
    generated_text = "".join([part["text"] for part in result.get("content", []) if "text" in part])
    return generated_text
