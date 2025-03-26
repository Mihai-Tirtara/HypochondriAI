import boto3
import json
import logging
from config.config import settings

def initialize_bedrock_client():
    """Create and return an Amazon Bedrock client"""
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        return bedrock
    except Exception as e:
        logging.error(f"Error initializing Bedrock client: {str(e)}")
        raise

def get_bedrock_response(prompt: str):
    """Get a response from the Amazon Bedrock model"""
    client = initialize_bedrock_client()
    try:
        payload = {
            "prompt": prompt,
            "max_gen_len": settings.MAX_TOKENS,
            "temperature": settings.TEMPERATURE,
            "top_p": settings.TOP_P
        }
        body = json.dumps(payload)
        response = client.invoke_model(
            modelId=settings.MODEL_ID,
            body=body,
            accept="application/json",
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        generated_text = response_body["generation"]
        return generated_text
    except Exception as e:
        logging.error(f"Error getting response from Bedrock model: {str(e)}")
        raise