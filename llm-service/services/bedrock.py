from typing import Optional
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

class BedrockService:
    def __init__(self, modelId : Optional[str] = None): 
        """
        Initialize Bedrock service with optional model_id
        
        Args:
            model_id: The model ID to use. If None, uses the default from settings.
        """
        
        self.client = initialize_bedrock_client()
        self.modelId = modelId or settings.MODEL_ID

    def prepare_request_body(self, prompt: str):
        """
        Prepare the request body based on the model ID
        
        Args:
            prompt: The text prompt
        
        Returns:
            Dict containing the formatted request body
        """
        if "anthropic.claude" in self.modelId:
            # Claude format
            claude_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": settings.MAX_TOKENS,
                "temperature": settings.TEMPERATURE,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            return claude_payload
        elif "meta" in self.modelId:
            # Meta format
            meta_payload = {
                "prompt": prompt,
                "max_gen_len": settings.MAX_TOKENS,
                "temperature": settings.TEMPERATURE,
                "top_p": settings.TOP_P
            }
            return meta_payload
        else:
            logging.error(f"Model ID {self.modelId} not recognized")
            raise ValueError(f"Model ID {self.modelId} not recognized")

    def prepare_response(self, response):
        """
        Prepare the response based on the model ID
        
        Args:
            response: The response from the model
        
        Returns:
            The generated text
        """
        try:
            

            if "anthropic.claude" in self.modelId:
            # Claude format
                return response.get('content', [{}])[0].get('text', '')
            elif "meta" in self.modelId:
            # Meta format
                return response["generation"]
            else:
            # Try some common response formats as fallback
                for key in ['completion', 'text', 'generated_text', 'output']:
                    if key in response:
                        return response[key]
        except Exception as e:
            logging.error(f"Error parsing response from Bedrock model: {str(response)}")
            raise        
        
    def get_response(self, prompt: str):
        """
        Get a formated response from the Amazon Bedrock model
        
        Args:
            prompt: The text prompt
        
        Returns:
            The formated generated text
        
        """
        try:
            payload = self.prepare_request_body(prompt)
            body = json.dumps(payload)
            response = self.client.invoke_model(
                modelId=self.modelId,
                body=body,
                accept="application/json",
                contentType="application/json"
            )
            response_body = json.loads(response['body'].read())
            generated_text = self.prepare_response(response_body)
            return generated_text
        except Exception as e:
            logging.error(f"Error getting response from Bedrock model: {str(e)}")
            raise    