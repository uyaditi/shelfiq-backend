import json
import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from services.bedrock import get_bedrock_client

router = APIRouter()

class Message(BaseModel):
    role: str      # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

SYSTEM_PROMPT = """You are an expert retail business strategist and AI copilot for store managers.
Help with inventory management, pricing strategy, shelf optimization, demand forecasting,
supplier negotiation, and customer experience. Be concise, use bullet points, and always
ground advice in practical retail context. When relevant, ask about store type or size."""

@router.post("/chat/general")
async def general_chat(request: ChatRequest):
    client = get_bedrock_client()

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": [m.dict() for m in request.messages]
    })

    try:
        response = client.invoke_model(
            modelId="anthropic.claude-sonnet-4-5",
            contentType="application/json",
            accept="application/json",
            body=body
        )
        result = json.loads(response["body"].read())
        return { "reply": result["content"][0]["text"] }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))