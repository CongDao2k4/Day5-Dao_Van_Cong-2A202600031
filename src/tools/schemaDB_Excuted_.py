import re
import psycopg
from langchain_core.tools import tool
from config import get_ctsv_database_url, get_database_url

# Cấu hình mapping giữa loại DB và URL/Mô tả
DATABASE_CONFIG = {
    "academic": {
        "url_getter": get_database_url,
        "description": "Dữ liệu học vụ, GPA, điểm số, học phí và danh sách sinh viên chính thống.",
        "env_var": "DATABASE_URL"
    },
    "ctsv_booking": {
        "url_getter": get_ctsv_database_url,
        "description": "Dữ liệu Phòng Cộng tác Sinh viên (CTSV), quản lý đặt phòng học, sự kiện ngoại khóa.",
        "env_var": "CTSV_DATABASE_URL"
    }
}

def _validate_select_readonly(query: str) -> str | None:
    """Kiểm tra tính an toàn của câu lệnh SQL."""
    clean_query = query.strip().lower()
    if not (clean_query.startswith("select") or clean_query.startswith("with")):
        return "Error: Security violation! Only SELECT or WITH (read-only) queries are permitted."
    
    forbidden_keywords = ["insert", "update", "delete", "drop", "truncate", "alter", "grant", "revoke", "create", "upsert"]
    for word in forbidden_keywords:
        if re.search(rf"\b{word}\b", clean_query):
            return f"Error: Security violation! '{word.upper()}' command is forbidden. This tool is READ-ONLY."
    return None

@tool
def list_databases_tool() -> str:
    """
    Liệt kê các database có sẵn trong hệ thống và mục đích của chúng.
    Hãy gọi tool này đầu tiên nếu bạn không chắc chắn cần truy vấn dữ liệu ở đâu.
    """
    info = "Các database khả dụng:\n"
    for db_type, config in DATABASE_CONFIG.items():
        info += f"- '{db_type}': {config['description']}\n"
    return info

@tool
def get_schema_tool(db_type: str) -> str:
    """
    Lấy schema (danh sách bảng và cột) của một database cụ thể.
    Tham số db_type: Phải là 'academic' hoặc 'ctsv_booking'.
    """
    if db_type not in DATABASE_CONFIG:
        return f"Error: Database '{db_type}' không tồn tại. Hãy dùng list_databases_tool để xem danh sách."
    
    url = DATABASE_CONFIG[db_type]["url_getter"]()
    if not url:
        return f"Error: Cấu hình cho {db_type} ({DATABASE_CONFIG[db_type]['env_var']}) chưa được thiết lập."

    try:
        schema_info = []
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                """)
                tables = [row[0] for row in cur.fetchall()]
                
                if not tables:
                    return f"Database '{db_type}' hiện không có bảng nào trong public schema."

                for table in tables:
                    cur.execute(f"""
                        SELECT column_name, data_type FROM information_schema.columns 
                        WHERE table_name = '{table}' ORDER BY ordinal_position
                    """)
                    columns = cur.fetchall()
                    col_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                    schema_info.append(f"Table: {table}\nColumns: {col_str}")
        
        return f"--- Schema cho DB: {db_type} ---\n\n" + "\n\n".join(schema_info)
    except Exception as e:
        return f"Error fetching schema for {db_type}: {str(e)}"

@tool
def execute_query_tool(db_type: str, query: str) -> str:
    """
    Thực thi truy vấn SQL (chỉ SELECT) trên database được chỉ định.
    Tham số db_type: 'academic' hoặc 'ctsv_booking'.
    Tham số query: Câu lệnh SQL SELECT hợp lệ.
    """
    if db_type not in DATABASE_CONFIG:
        return f"Error: Database '{db_type}' không tồn tại."
    
    err = _validate_select_readonly(query)
    if err:
        return err
        
    url = DATABASE_CONFIG[db_type]["url_getter"]()
    try:
        with psycopg.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description is None:
                    return "Query executed successfully, but returned no data."
                
                columns = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                
                if not results:
                    return f"Kết quả từ {db_type}: 0 dòng."
                
                res_output = [" | ".join(columns)]
                res_output.append("-" * len(res_output[0]))
                for row in results:
                    res_output.append(" | ".join([str(val) for val in row]))
                
                return f"--- Kết quả từ {db_type} ({len(results)} dòng) ---\n" + "\n".join(res_output)
    except Exception as e:
        return f"Database Error ({db_type}): {str(e)}"
