"""
Core pipeline:
  1. Build prompts from RDS schema
  2. Call Gemini to generate SQL
  3. Execute SQL against RDS
  4. Call Gemini again to produce a user-friendly response
"""

import os
import json
import re
import pandas as pd
from typing import List, Dict, Tuple

import google.generativeai as genai

from db import engine                          # ← use db.py's engine directly
from services.db_chat.prompt import get_rds_prompts


# ---------------------------------------------------------------------------
# Gemini setup
# ---------------------------------------------------------------------------

def _get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash-lite")


# ---------------------------------------------------------------------------
# Step 1 – Gemini generates SQL
# ---------------------------------------------------------------------------

def call_gemini_for_sql(system_prompt: str, user_prompt: str) -> dict:
    model = _get_gemini_model()
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    response = model.generate_content(full_prompt)

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON.\nError: {e}\nRaw:\n{raw}")


# ---------------------------------------------------------------------------
# Step 2 – Execute SQL on RDS
# ---------------------------------------------------------------------------

def run_rds_queries(sql_items: List[Dict[str, str]]) -> List[Tuple[str, pd.DataFrame]]:
    if not sql_items:
        return []

    results = []

    with engine.connect() as conn:                # ← directly use imported engine
        for item in sql_items:
            query = item.get("query", "").strip()
            description = item.get("description", "")

            if not query:
                continue

            # Safety: only allow SELECT
            if not query.lstrip().upper().startswith("SELECT"):
                results.append((
                    f"{description}\n⚠️ Blocked: only SELECT queries are permitted.",
                    pd.DataFrame()
                ))
                continue

            try:
                df = pd.read_sql_query(query, conn)
                results.append((description, df))
            except Exception as e:
                results.append((f"{description}\n⚠️ Error: {str(e)}", pd.DataFrame()))

    return results


# ---------------------------------------------------------------------------
# Step 3 – Gemini summarises results in plain English
# ---------------------------------------------------------------------------

def call_gemini_for_response(
    original_question: str,
    reasoning: str,
    results: List[Tuple[str, pd.DataFrame]]
) -> str:
    model = _get_gemini_model()

    result_blocks = []
    for i, (desc, df) in enumerate(results, start=1):
        if not df.empty:
            result_blocks.append(f"Result {i} – {desc}\n{df.to_markdown(index=False)}")
        else:
            result_blocks.append(f"Result {i} – {desc}\n(No data returned)")

    results_text = "\n\n".join(result_blocks) if result_blocks else "No results were returned."

    summarize_prompt = f"""You are a helpful retail data analyst assistant.
A user asked: "{original_question}"

Approach taken: {reasoning}

Query results:
{results_text}

Write a clear, friendly, concise response that:
1. Directly answers the question using the data above.
2. Highlights key numbers or trends.
3. Uses plain language — no SQL or technical jargon.
4. Is conversational and helpful in tone.
5. If results are empty, politely say no matching data was found.

Do NOT repeat the raw table data — summarise and interpret it."""

    response = model.generate_content(summarize_prompt)
    return response.text.strip()


# ---------------------------------------------------------------------------
# Step 4 – Format structured output
# ---------------------------------------------------------------------------

def _df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No data available._"
    return df.to_markdown(index=False, tablefmt="github")


def format_full_response(
    reasoning: str,
    results: List[Tuple[str, pd.DataFrame]],
    gemini_summary: str
) -> dict:
    tables = []
    for description, df in results:
        tables.append({
            "description": description,
            "data": df.to_dict(orient="records"),
            "markdown": _df_to_markdown(df)
        })

    return {
        "summary": gemini_summary,
        "tables": tables,
        "reasoning": reasoning
    }


# ---------------------------------------------------------------------------
# Main entrypoint — called by the route
# ---------------------------------------------------------------------------

async def run_rds_query(question: str) -> dict:
    system_prompt, user_prompt = get_rds_prompts(question)
    parsed = call_gemini_for_sql(system_prompt, user_prompt)

    reasoning = parsed.get("reasoning", "")
    sql_items = parsed.get("sql", [])

    results = run_rds_queries(sql_items)
    gemini_summary = call_gemini_for_response(question, reasoning, results)

    return format_full_response(reasoning, results, gemini_summary)