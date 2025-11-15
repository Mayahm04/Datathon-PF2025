import requests
from requests_aws4auth import AWS4Auth
import boto3

region = "us-west-2"
service = "aoss"
host = "https://j5ndx5b203f1iaom9pz5.us-west-2.aoss.amazonaws.com"  # ✅ ton vrai endpoint ici
index_name = "law-index"

session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# ---- Schéma d’un index vectoriel compatible Bedrock ----
payload = {
    "settings": {
        "index": {
            "knn": True
        }
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "metadata": {"type": "keyword"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1536,  # Amazon Titan v2 embedding size
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "faiss"
                }
            }
        }
    }
}

url = f"{host}/{index_name}"
response = requests.put(url, auth=awsauth, json=payload, headers={"Content-Type": "application/json"})

if response.status_code in [200, 201]:
    print(f"✅ Index '{index_name}' created successfully!")
else:
    print(f"❌ Failed to create index: {response.status_code} - {response.text}")
