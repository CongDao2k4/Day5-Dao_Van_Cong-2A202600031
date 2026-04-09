from pathlib import Path
from typing import Any, Dict, List

from langchain_core.tools import tool


def load_template(filename: str) -> str:
    """Load an email template from ``src/templates/`` (next to the ``tools`` package)."""
    template_path = Path(__file__).resolve().parent.parent / 'templates' / filename
    if not template_path.exists():
        raise FileNotFoundError(f'Template not found at {template_path}')
    return template_path.read_text(encoding='utf-8')


@tool
def email_draft_tool(
    students: List[Dict[str, Any]],
    email_template: str,
    subject_template: str = 'Notification from VinUni - {{mssv}}',
) -> List[Dict[str, str]]:
    """
    Draft personalized emails for a list of students with flexible content (Tuition, Academic Results, Program info).

    Supports merge fields corresponding to database fields:
    - Basic: {{full_name}}, {{mssv}}, {{email}}, {{major}}, {{cohort}}
    - Tuition: {{amount_due_vnd}}, {{amount_paid_vnd}}, {{outstanding_tuition_vnd}}, {{due_date}}
    - Academic: {{term_gpa}}, {{credits_registered}}, {{credits_earned}}, {{term_code}}

    Args:
        students: High-level list containing student info and related data (GPA, Tuition...).
        email_template: Email body template containing {{field_name}} placeholders.
        subject_template: Email subject template.

    Returns:
        List[Dict]: A list of complete personalized email drafts.
    """
    drafts = []
    for student in students:
        # Initialize body and subject from templates
        body = email_template
        subject = subject_template

        # Clone student data to avoid side effects
        data = student.copy()

        # Calculate outstanding tuition if info is available
        if 'amount_due_vnd' in data and 'amount_paid_vnd' in data:
            data['outstanding_tuition_vnd'] = data['amount_due_vnd'] - data['amount_paid_vnd']

        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'

            # Format display data based on field type/name
            display_value = value
            if value is None:
                display_value = 'N/A'
            elif isinstance(value, (int, float)):
                if any(k in key.lower() for k in ['amount', 'tuition', 'vnd']):
                    # Currency format: 1,000,000
                    display_value = f'{int(value):,}'
                elif 'gpa' in key.lower():
                    # GPA format: 3.80
                    display_value = f'{value:.2f}'

            # Replace placeholders in both body and subject
            body = body.replace(placeholder, str(display_value))
            subject = subject.replace(placeholder, str(display_value))

        drafts.append({
            'mssv': str(data.get('mssv', 'N/A')),
            'email': str(data.get('email', 'N/A')),
            'subject': subject,
            'body': body,
        })
    return drafts
