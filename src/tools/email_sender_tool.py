import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List

from langchain_core.tools import tool

from config import get_smtp_config

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
