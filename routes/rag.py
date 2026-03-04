import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.bedrock import get_bedrock_agent_client

router = APIRouter()

class RAGRequest(BaseModel):
    query: str

PROMPT_TEMPLATE = """You are a retail data analyst with access to live store data.
Use the store data below to answer the query with specific numbers, SKUs, and 
actionable recommendations. If data is insufficient, say so clearly.

Store Data:
$search_results$

Query: $query$"""

@router.post("/chat/rag")
async def rag_chat(request: RAGRequest):
    client = get_bedrock_agent_client()
    region = os.getenv("AWS_REGION")
    kb_id = os.getenv("BEDROCK_KB_ID")

    try:
        response = client.retrieve_and_generate(
            input={"text": request.query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{region}::foundation-model/anthropic.claude-sonnet-4-5",
                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": PROMPT_TEMPLATE
                        }
                    },
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5  # how many KB chunks to retrieve
                        }
                    }
                }
            }
        )

        citations = []
        for citation in response.get("citations", []):
            for ref in citation.get("retrievedReferences", []):
                citations.append({
                    "text": ref["content"]["text"][:200],   # snippet preview
                    "source": ref["location"].get("s3Location", {}).get("uri", "")
                })

        return {
            "reply": response["output"]["text"],
            "citations": citations   # send to frontend optionally
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))