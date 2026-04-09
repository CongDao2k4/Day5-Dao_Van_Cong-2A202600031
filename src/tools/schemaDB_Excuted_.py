import re

import psycopg
from langchain_core.tools import tool

from config import get_ctsv_database_url, get_database_url


def _validate_select_readonly(query: str) -> str | None:
    """Return error message if query is not allowed, else None."""
    clean_query = query.strip().lower()
    if not (clean_query.startswith("select") or clean_query.startswith("with")):
        return "Error: Security violation! Only SELECT or WITH (read-only) queries are permitted."
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "truncate",
        "alter",
        "grant",
        "revoke",
        "create",
        "upsert",
    ]
    for word in forbidden_keywords:
        if re.search(rf"\b{word}\b", clean_query):
            return f"Error: Security violation! '{word.upper()}' command is strictly forbidden. This tool is READ-ONLY."
    return None


def _fetch_schema(url: str) -> str:
    schema_info = []
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            tables = [row[0] for row in cur.fetchall()]

            if not tables:
                return "No tables found in the public schema."

            for table in tables:
                cur.execute(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                col_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                schema_info.append(f"Table: {table}\nColumns: {col_str}")

    return "\n\n".join(schema_info)


def _execute_select(url: str, query: str) -> str:
    err = _validate_select_readonly(query)
    if err:
        return err
    try:
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description is None:
                    return "Query executed successfully, but returned no data."
                columns = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                if not results:
                    return "Query returned 0 rows."
                res_output = [" | ".join(columns)]
                res_output.append("-" * len(res_output[0]))
                for row in results:
                    res_output.append(" | ".join([str(val) for val in row]))
                return "\n".join(res_output)
    except Exception as e:
        return f"Database Error: {str(e)}"


@tool
def get_db_schema_tool() -> str:
    """
    Schema của DB Academic (DATABASE_URL): academic_terms, students, student_term_academics,
    tuition_invoices, email_send_log, view v_student_current_term_snapshot.
    Dùng trước khi viết SQL cho học vụ / GPA / học phí.
    """
    url = get_database_url()
    if not url:
        return "Error: DATABASE_URL is not set in environment variables."
    try:
        return _fetch_schema(url)
    except Exception as e:
        return f"Error fetching schema: {str(e)}"


@tool
def get_ctsv_db_schema_tool() -> str:
    """
    Schema của DB CTSV đặt phòng (CTSV_DATABASE_URL): study_rooms, room_bookings, view v_room_upcoming_bookings.
    Khóa nối với DB academic: room_bookings.student_mssv = students.mssv (hai URI khác nhau — agent truy vấn từng DB rồi ghép).
    """
    url = get_ctsv_database_url()
    if not url:
        return "Error: CTSV_DATABASE_URL is not set in environment variables."
    try:
        return _fetch_schema(url)
    except Exception as e:
        return f"Error fetching schema: {str(e)}"


@tool
def sql_query_tool(query: str) -> str:
    """
    Thực thi SELECT (read-only) trên DB Academic — biến môi trường DATABASE_URL.
    """
    url = get_database_url()
    if not url:
        return "Error: DATABASE_URL is not set."
    return _execute_select(url, query)


@tool
def sql_ctsv_query_tool(query: str) -> str:
    """
    Thực thi SELECT (read-only) trên DB CTSV đặt phòng — biến môi trường CTSV_DATABASE_URL.
    """
    url = get_ctsv_database_url()
    if not url:
        return "Error: CTSV_DATABASE_URL is not set."
    return _execute_select(url, query)
