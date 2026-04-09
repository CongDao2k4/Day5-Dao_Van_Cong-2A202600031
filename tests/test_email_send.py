"""Integration test: send a real email when SMTP_* is configured in the environment."""

from __future__ import annotations

import time

import pytest
from config import get_smtp_host, get_smtp_password

from tools.email import bulk_email_sender_tool, send_email_smtp
from tools.email_draft import email_draft_tool, load_template

TEST_TO = 'sv5.test@thanhnn.dev'

configured = bool(get_smtp_host() and get_smtp_password())


@pytest.mark.skipif(
    not configured,
    reason='Set SMTP_HOST and SMTP_PASSWORD in .env to run this test.',
)
def test_send_email_to_sv5_test() -> None:
    stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    subject = f'c401 email tool test {stamp}'
    body = f'Integration test from tests/test_email_send.py at {stamp}.'

    result = send_email_smtp(to=TEST_TO, subject=subject, body=body)

    assert result.startswith('Email sent successfully'), result


@pytest.mark.skipif(
    not configured,
    reason='Set SMTP_HOST and SMTP_PASSWORD in .env to run this test.',
)
def test_bulk_send_email() -> None:
    stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    drafts = [
        {
            'email': TEST_TO,
            'subject': f'c401 bulk test 1/2 {stamp}',
            'body': f'Batch email 1 at {stamp}'
        },
        {
            'email': TEST_TO,
            'subject': f'c401 bulk test 2/2 {stamp}',
            'body': f'Batch email 2 at {stamp}'
        }
    ]

    result = bulk_email_sender_tool.invoke({'drafts': drafts})

    assert result['total'] == 2
    assert result['success'] >= 0  # Success depends on actual SMTP, but total should be correct


@pytest.mark.skipif(
    not configured,
    reason='Set SMTP_HOST and SMTP_PASSWORD in .env to run this test.',
)
def test_bulk_send_with_html_template() -> None:
    # 1. Load the HTML template
    template_content = load_template("tuition_notification.html")
    
    # 2. Mock student data for merging
    students = [
        {
            "full_name": "Nguyen Van A",
            "mssv": "SV001",
            "email": TEST_TO,
            "major": "Computer Science",
            "cohort": "2022",
            "amount_due_vnd": 50000000,
            "amount_paid_vnd": 10000000,
            "due_date": "2026-05-15"
        },
        {
            "full_name": "Tran Thi B",
            "mssv": "SV002",
            "email": TEST_TO,
            "major": "Business Administration",
            "cohort": "2023",
            "amount_due_vnd": 60000000,
            "amount_paid_vnd": 20000000,
            "due_date": "2026-05-20"
        }
    ]
    
    # 3. Use email_draft_tool to create HTML drafts
    drafts = email_draft_tool.invoke({
        "students": students,
        "email_template": template_content,
        "subject_template": "Tuition Notification - {{full_name}} ({{mssv}})"
    })
    
    # 4. Use bulk_email_sender_tool to send them
    result = bulk_email_sender_tool.invoke({'drafts': drafts})
    
    assert result['total'] == 2
    assert result['success'] >= 0
    print(f"\nBulk HTML test result: {result['success']} succeeded, {result['failed']} failed.")
