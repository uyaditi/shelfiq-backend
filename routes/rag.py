from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from services.db_chat.get_response import run_rds_query
from services.db_chat.rds_schema import get_all_table_names

router = APIRouter()

# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RDSChatRequest(BaseModel):
    query: str

class TableResult(BaseModel):
    description: str
    data: list
    markdown: str


class RDSChatResponse(BaseModel):
    summary: str        # Gemini's plain-English answer
    tables: List[TableResult]
    reasoning: str      # How Gemini approached it (hide in frontend if preferred)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/chat/agent", response_model=RDSChatResponse)
async def rds_chat(request: RDSChatRequest):
    """
    Drop-in replacement for the old Bedrock /chat/agent endpoint.
    Accepts a natural-language question, queries RDS via Gemini-generated SQL,
    and returns a structured + summarised response.
    """
    try:
        result = await run_rds_query(
            question=request.query
        )
        return RDSChatResponse(
            summary=result["summary"],
            tables=[TableResult(**t) for t in result["tables"]],
            reasoning=result["reasoning"]
        )
    except Exception as e:
        print(f"[RDS Chat Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rds/tables")
async def list_tables():
    """Returns all table names from RDS — useful for frontend table pickers."""
    try:
        return {"tables": get_all_table_names()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))