from typing import Any, Dict, List
from langchain_core.tools import tool

@tool
def email_draft_tool(
    students: List[Dict[str, Any]], 
    email_template: str, 
    subject_template: str = 'Thông báo từ VinUni - {{mssv}}'
) -> List[Dict[str, str]]:
    """
    Soạn thảo email cá nhân hóa cho danh sách sinh viên với nội dung linh hoạt (Học phí, Kết quả học tập, Chương trình học).

    Hỗ trợ các merge fields tương ứng với dữ liệu database:
    - Cơ bản: {{full_name}}, {{mssv}}, {{email}}, {{major}}, {{cohort}}
    - Học phí: {{amount_due_vnd}}, {{amount_paid_vnd}}, {{outstanding_tuition_vnd}}, {{due_date}}
    - Kết quả học tập: {{term_gpa}}, {{credits_registered}}, {{credits_earned}}, {{term_code}}

    Args:
        students: Danh sách chứa thông tin sinh viên và dữ liệu liên quan (GPA, Học phí...).
        email_template: Nội dung email mẫu có chứa các placeholder {{field_name}}.
        subject_template: Tiêu đề email mẫu.

    Returns:
        List[Dict]: Danh sách các bản nháp email hoàn chỉnh.
    """
    drafts = []
    for student in students:
        # Xử lý nội dung (Body) và tiêu đề (Subject)
        body = email_template
        subject = subject_template

        # Tổng hợp tất cả các key
        data = student.copy()
        
        # Tính toán nợ học phí nếu có đủ thông tin
        if 'amount_due_vnd' in data and 'amount_paid_vnd' in data:
            data['outstanding_tuition_vnd'] = data['amount_due_vnd'] - data['amount_paid_vnd']

        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            
            # Format dữ liệu hiển thị
            display_value = value
            if value is None:
                display_value = 'N/A'
            elif isinstance(value, (int, float)):
                if 'amount' in key.lower() or 'tuition' in key.lower() or 'vnd' in key.lower():
                    display_value = f'{int(value):,}'
                elif 'gpa' in key.lower():
                    display_value = f'{value:.2f}'
            
            body = body.replace(placeholder, str(display_value))
            subject = subject.replace(placeholder, str(display_value))
        
        drafts.append({
            'mssv': str(data.get('mssv', 'N/A')),
            'email': str(data.get('email', 'N/A')),
            'subject': subject,
            'body': body
        })
    return drafts
