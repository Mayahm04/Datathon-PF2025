import boto3
from config import S3_REGION

# Initialisation des clients AWS
s3_client = boto3.client("s3", region_name=S3_REGION)
bedrock_client = boto3.client("bedrock-runtime", region_name=S3_REGION)
aoss_client = boto3.client("opensearchserverless", region_name=S3_REGION)
bedrock_agent_client = boto3.client("bedrock-agent", region_name=S3_REGION)
