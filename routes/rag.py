import os
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.bedrock import get_bedrock_agent_client

router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    session_id: str = None  # Optional: Pass this from the frontend to remember conversation history

@router.post("/chat/agent")
async def agent_chat(request: AgentRequest):
    client = get_bedrock_agent_client()
    agent_id = os.getenv("BEDROCK_AGENT_ID")
    agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
    
    # Agents require a session ID to remember chat history. 
    # If the frontend doesn't provide one, generate a new one.
    session_id = request.session_id or str(uuid.uuid4())

    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=request.query
        )

        completion_text = ""
        
        # The agent returns a stream of events. We need to loop through and extract the text chunks.
        for event in response.get("completion"):
            if "chunk" in event:
                chunk = event["chunk"]
                completion_text += chunk["bytes"].decode("utf-8")
            # You can also catch "trace" events here if you want to log the exact SQL query the agent wrote!

        return {
            "reply": completion_text,
            "session_id": session_id
        }

    except Exception as e:
        print(f"Agent Error: {e}") # Helpful for backend debugging
        raise HTTPException(status_code=500, detail=str(e))