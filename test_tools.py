import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print("Error: psycopg not found. Please run 'pip install psycopg[binary]'")
    sys.exit(1)

from config import get_database_url
from tools.email import email_draft_tool, email_sender_tool

def test_workflow():
    db_url = get_database_url()
    print(f"Connecting to: {db_url[:20]}...")
    
    try:
        with psycopg.connect(db_url, row_factory=dict_row, connect_timeout=10) as conn:
            # 1. Lấy dữ liệu mẫu từ VIEW snapshot
            students = conn.execute("SELECT * FROM v_student_current_term_snapshot LIMIT 2").fetchall()
            
            if not students:
                print("No students found in DB.")
                return

            print(f"Found {len(students)} students.")
            for s in students:
                print(f"- {s['full_name']} ({s['mssv']}) - Email: {s['email']}")

            # 2. Chạy email_draft_tool
            template = "Chào {{full_name}}, kết quả học kỳ của bạn là: GPA {{current_term_gpa}}. Nợ học phí: {{outstanding_tuition_vnd}} VND."
            drafts = email_draft_tool.invoke({
                "students": students, 
                "email_template": template,
                "subject_template": "[VinUni] Kết quả học tập - {{mssv}}"
            })
            
            print("\nDrafts created:")
            for d in drafts:
                print(f"Subject: {d['subject']}")
                print(f"Body: {d['body']}")
                print("-" * 20)

            # 3. Chạy email_sender_tool
            print("\nSending emails...")
            result = email_sender_tool.invoke({"drafts": drafts})
            print(f"Result: {result}")

    except Exception as e:
        print(f"Workflow error: {e}")

if __name__ == "__main__":
    test_workflow()
