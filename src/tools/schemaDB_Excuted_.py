import os
import psycopg
from langchain_core.tools import tool
from config import get_database_url

@tool
def get_db_schema_tool() -> str:
    """
    Get the schema of the database including table names and column names.
    Useful for the agent to understand the database structure before generating SQL.
    """
    url = get_database_url()
    if not url:
        return "Error: DATABASE_URL is not set in environment variables."
    
    schema_info = []
    try:
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                # Lấy danh sách các bảng trong schema public
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
                    # Lấy thông tin cột cho từng bảng
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
    except Exception as e:
        return f"Error fetching schema: {str(e)}"

@tool
def sql_query_tool(query: str) -> str:
    """
    Execute a SQL SELECT query against the database and return the results.
    Input: A valid SQL SELECT query string.
    Output: The query results as a formatted string or an error message.
    """
    url = get_database_url()
    if not url:
        return "Error: DATABASE_URL is not set."
    
    # --- CHẾ ĐỘ READ-ONLY NGHIÊM NGẶT ---
    # 1. Làm sạch câu lệnh (bỏ khoảng trắng và xuống dòng ở đầu/cuối)
    clean_query = query.strip().lower()
    
    # 2. Chỉ cho phép bắt đầu bằng SELECT hoặc WITH (Common Table Expressions)
    if not (clean_query.startswith("select") or clean_query.startswith("with")):
        return "Error: Security violation! Only SELECT or WITH (read-only) queries are permitted."
    
    # 3. Chặn các từ khóa nguy hiểm xuất hiện ở bất kỳ đâu trong câu lệnh
    forbidden_keywords = ["insert", "update", "delete", "drop", "truncate", "alter", "grant", "revoke", "create", "upsert"]
    for word in forbidden_keywords:
        # Dùng regex hoặc ranh giới từ để tránh chặn nhầm (ví dụ: bảng "student_updates")
        import re
        if re.search(rf"\b{word}\b", clean_query):
            return f"Error: Security violation! '{word.upper()}' command is strictly forbidden. This tool is READ-ONLY."
        
    try:
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                
                # Check if there are results to fetch
                if cur.description is None:
                    return "Query executed successfully, but returned no data."
                
                columns = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                
                if not results:
                    return "Query returned 0 rows."
                
                # Format kết quả dạng bảng CSV-like để Agent dễ đọc
                res_output = [ " | ".join(columns) ]
                res_output.append("-" * (len(res_output[0]))) # Separator line
                
                for row in results:
                    res_output.append(" | ".join([str(val) for val in row]))
                
                row_count = len(results)
                final_output = "\n".join(res_output)
                # return f"Found {row_count} rows:\n\n{final_output}"
                return final_output
                
    except Exception as e:
        return f"Database Error: {str(e)}"
