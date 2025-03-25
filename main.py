import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import boto3
import json
from typing import Optional, List, Dict, Any

load_dotenv()

app = FastAPI(title="Health Anxiety Management system", description="A LLM service to provide support for people with health anxiety", version="0.1")


#Intialize Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") 
)

#Define model for input
class HealthQuery(BaseModel):
    symptoms: str
    user_context: Optional[str] = None

#Define model for output
class HealthResponse(BaseModel):
    response: str

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/analyze-symptoms", response_model=HealthResponse)
async def analyze_symptoms(query: HealthQuery):
   try:
       prompt = f"""
        You are a helpful health assistant designed to provide calm, factual information about common symptoms.
        
        User symptoms: {query.symptoms}
        
        User context: {query.user_context or "No additional context provided."}
        
        Please provide a calm and reassuring response that:
        1. Acknowledges the user's concern
        2. Provides factual information about these symptoms
        3. Offers perspective on common vs. serious causes
        4. Suggests when medical attention might be appropriate
        5. Provides some self-care tips if applicable
        
        Always maintain a balanced, educational tone without dismissing concerns or causing additional anxiety.
        """
       payload = {
           "prompt": prompt,
           "max_gen_len": 512,
           "temperature": 0.7,
           "top_p": 0.9
       }

       body = json.dumps(payload) 
       
       response = bedrock.invoke_model(
              modelId=os.getenv("AWS_MODEL_NAME"),
              body=body,
              accept="application/json",
              contentType="application/json"
         )
       response_body = json.loads(response['body'].read())
       generated_text = response_body["generation"]
       return HealthResponse(response=generated_text)
   except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)   