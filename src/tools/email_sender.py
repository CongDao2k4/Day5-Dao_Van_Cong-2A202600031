import uuid
from typing import Any, Dict, List

from langchain_core.tools import tool

# Import hàm gửi mail đã được chuẩn hóa từ email.py
from tools.email import send_email_smtp


@tool
def email_sender_tool(drafts: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Thực hiện gửi email hàng loạt dựa trên danh sách bản nháp bằng cách sử dụng 
    hàm gửi mail chuẩn từ email.py.

    Chức năng: Lặp qua danh sách bản nháp và thực hiện lệnh gửi.
    Lưu ý: Tool này nên được gọi sau bước xác nhận HIL trên UI.

    Args:
        drafts: Danh sách bản nháp email (mỗi bản có email, subject, body).

    Returns:
        Dict: Báo cáo kết quả gửi chi tiết.
    """
    batch_id = str(uuid.uuid4())
    success_count = 0
    fail_count = 0
    results = []

    for draft in drafts:
        recipient = draft.get('email', '').strip()
        subject = draft.get('subject', 'No Subject')
        body = draft.get('body', '')

        if not recipient:
            fail_count += 1
            results.append({'status': 'failed', 'error': 'Missing recipient address'})
            continue

        # Gọi hàm gửi chuẩn từ email.py
        result_msg = send_email_smtp(to=recipient, subject=subject, body=body)

        if result_msg.startswith('Email sent successfully'):
            success_count += 1
            results.append({'email': recipient, 'status': 'sent'})
        else:
            fail_count += 1
            results.append({'email': recipient, 'status': 'failed', 'error': result_msg})

    return {
        'batch_id': batch_id,
        'total': len(drafts),
        'success': success_count,
        'failed': fail_count,
        'results': results,
        'message': f'Đã xử lý xong batch {batch_id}. Thành công: {success_count}, Thất bại: {fail_count}'
    }
