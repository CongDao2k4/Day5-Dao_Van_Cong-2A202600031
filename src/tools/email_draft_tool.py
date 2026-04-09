import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from langchain_core.tools import tool

from config import get_smtp_config


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


@tool
def email_sender_tool(drafts: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Thực hiện gửi email hàng loạt (SMTP/Email Service) dựa trên danh sách bản nháp.

    Ưu tiên sử dụng cấu hình SMTP từ môi trường nếu có. 
    Nếu không, sẽ hoạt động ở chế độ giả lập và trả về kết quả dự kiến.

    Args:
        drafts: Danh sách bản nháp email cần gửi.

    Returns:
        Dict: Báo cáo kết quả gửi (số lượng thành công, thất bại, chi tiết lỗi nếu có).
    """
    smtp_cfg = get_smtp_config()
    batch_id = str(uuid.uuid4())
    success_count = 0
    fail_count = 0
    details = []

    # Kiểm tra cấu hình SMTP
    use_real_smtp = all([smtp_cfg['host'], smtp_cfg['user'], smtp_cfg['pass']])
    server = None

    try:
        if use_real_smtp:
            server = smtplib.SMTP(smtp_cfg['host'], smtp_cfg['port'])
            server.starttls()
            server.login(smtp_cfg['user'], smtp_cfg['pass'])

        for draft in drafts:
            recipient = draft.get('email')
            try:
                if use_real_smtp:
                    msg = MIMEMultipart()
                    msg['From'] = smtp_cfg['user']
                    msg['To'] = recipient
                    msg['Subject'] = draft.get('subject')
                    msg.attach(MIMEText(draft.get('body', ''), 'plain'))
                    server.send_message(msg)
                
                success_count += 1
                details.append({'email': recipient, 'status': 'sent'})
            except Exception as e:
                fail_count += 1
                details.append({'email': recipient, 'status': 'failed', 'error': str(e)})

    finally:
        if server:
            server.quit()

    return {
        'batch_id': batch_id,
        'total': len(drafts),
        'success': success_count,
        'failed': fail_count,
        'mode': 'REAL_SMTP' if use_real_smtp else 'PROTOTYPE_SIMULATION',
        'results': details
    }
