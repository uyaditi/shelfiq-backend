import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

import google.generativeai as genai

router = APIRouter()


class Message(BaseModel):
    role: str       # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


SYSTEM_PROMPT = """You are an expert retail business strategist and AI copilot for store managers.
Help with inventory management, pricing strategy, shelf optimization, demand forecasting,
supplier negotiation, and customer experience. Be concise, use bullet points, and always
ground advice in practical retail context. When relevant, ask about store type or size."""


def _get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )


@router.post("/chat/general")
async def general_chat(request: ChatRequest):
    try:
        model = _get_gemini_model()

        # Convert messages to Gemini format
        # Gemini uses "user" and "model" (not "assistant")
        history = []
        for m in request.messages[:-1]:   # all but the last message go into history
            history.append({
                "role": "model" if m.role == "assistant" else "user",
                "parts": [m.content]
            })

        # The last message is the one we send now
        last_message = request.messages[-1].content

        chat = model.start_chat(history=history)
        response = chat.send_message(last_message)

        return {"reply": response.text.strip()}

    except Exception as e:
        print(f"General Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))