"""
Fetches schema and sample rows from Amazon RDS (PostgreSQL).
"""

import os
import pandas as pd
from sqlalchemy import text, create_engine
from db import SessionLocal
from db import engine, SessionLocal

def _get_engine():
    return engine

def get_all_table_names() -> list[str]:
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        return [row[0] for row in result.fetchall()]
    finally:
        db.close()


def get_rds_schema_info() -> str:
    db = SessionLocal()
    try:
        all_tables = get_all_table_names()

        schema_blocks = []
        for table in all_tables:
            col_result = db.execute(text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table
                ORDER BY ordinal_position;
            """), {"table": table})
            cols = col_result.fetchall()
            col_lines = [f"  - {col[0]} ({col[1]})" for col in cols]
            schema_blocks.append(
                f"Table: {table}\nColumns:\n" + "\n".join(col_lines)
            )
        return "\n\n".join(schema_blocks)
    finally:
        db.close()


def get_rds_table_samples(max_rows: int = 3) -> str:
    engine = _get_engine()
    all_tables = get_all_table_names()
    
    blocks = []
    with engine.connect() as conn:
        for table in all_tables:
            df = pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {max_rows}', conn)
            blocks.append(f"Sample rows from table '{table}':\n{df.to_string(index=False)}")
    return "\n\n".join(blocks)