import boto3
from botocore.exceptions import ClientError
import os
import json
import logging

# Configure the logger
logger = logging.getLogger()
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logger.setLevel(log_level)

# Initialize Bedrock client
bart = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# Configuration: Update with your IDs
REGION_ID = os.environ['REGION']
FOUNDANTION_MODEL_ID = os.environ['FOUNDANTION_MODEL_ID']  # Replace with your model
KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']                      # Replace with your KB ID
MODEL_ARN = f"arn:aws:bedrock:{REGION_ID}::foundation-model/{FOUNDANTION_MODEL_ID}"

def lambda_handler(event, context):
    """
    Lambda handler for Bedrock KB queries.
    Expects event["text"] containing the user's query.
    """
    user_query = event.get("message", "")
    logger.info(f"user_query= {user_query}")

    if "body" in event: # API Gateway sends body as a string
        user_query = event["body"] if json.loads( event["body"] ) else user_query
        
    if not user_query:
        logger.exception("No query text provided in 'text' field.") # Logs exception details automatically
        return { 
            "statusCode": 400,
            "error": "No query text provided in 'text' field."
        }

    return chat(user_query)


def chat(query_text):
    """
    Calls Bedrock retrieve-and-generate on the Knowledge Base and
    returns structured JSON including citations.
    """
    try:
        response = bart.retrieve_and_generate(
            input={"text": query_text},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                    "modelArn": MODEL_ARN
                }
            }
        )

        responseOutput = response.get("output", {})
        
        logger.info(f"responseOutput= {responseOutput}")

        # Extract the main generated text
        generated_text = responseOutput.get("text", "No response from model.")

        # Extract citations for traceability
        citations = []
        for citation in response.get("citations", []):
            citation_text = citation.get("generatedResponsePart", {}).get("textResponsePart", {}).get("text")
            retrieved_refs = citation.get("retrievedReferences", [])
            refs_info = []
            for ref in retrieved_refs:
                refs_info.append({
                    "text": ref.get("content", {}).get("text"),
                    "s3_uri": ref.get("location", {}).get("s3Location", {}).get("uri")
                })
            citations.append({
                "generated_text": citation_text,
                "retrievedReferences": refs_info
            })

        logger.info(f"generated_text= {generated_text}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "response": generated_text,
                "citations": citations
            }),
            "headers": { 
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, PUT, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
            }
        }
    
    except ClientError as e:
        logger.exception(f"ClientError: {e}") # Logs exception details automatically
        return {"error": f"ClientError: {e}"}
    except Exception as e:
        logger.exception(f"Exception: {e}") # Logs exception details automatically
        return {"error": f"Exception: {e}"}