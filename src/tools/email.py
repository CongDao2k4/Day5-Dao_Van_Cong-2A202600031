"""SMTP email sending for LangGraph agents (TLS via STARTTLS or SMTP_SSL)."""

from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from config import (
    TlsMode,
    get_smtp_from,
    get_smtp_host,
    get_smtp_password,
    get_smtp_port,
    get_smtp_tls_mode,
    get_smtp_user,
)
from langchain_core.tools import tool


def _smtp_settings() -> dict[str, str | int | TlsMode]:
    host = get_smtp_host()
    if not host:
        msg = 'SMTP_HOST is not set'
        raise ValueError(msg)

    tls_mode = get_smtp_tls_mode()
    port_raw = get_smtp_port()
    if port_raw:
        port = int(port_raw)
    else:
        port = 465 if tls_mode == 'ssl' else 587

    user = get_smtp_user() or ''
    password = get_smtp_password() or ''
    from_addr = get_smtp_from() or user
    if not from_addr:
        msg = 'SMTP_FROM or SMTP_USER must be set for the From address'
        raise ValueError(msg)

    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'from_addr': from_addr,
        'tls_mode': tls_mode,
    }


def send_email_smtp(
    to: str,
    subject: str,
    body: str,
) -> str:
    """Send one plain-text email using env SMTP settings. Returns a status message."""
    to = to.strip()
    if not to:
        return 'Error: recipient address (to) is empty.'

    try:
        cfg = _smtp_settings()
    except ValueError as e:
        return f'Error: {e}'

    host = cfg['host']
    port = int(cfg['port'])
    user = str(cfg['user'])
    password = str(cfg['password'])
    from_addr = str(cfg['from_addr'])
    tls_mode = cfg['tls_mode']

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to
    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        if tls_mode == 'ssl':
            with smtplib.SMTP_SSL(host, port, timeout=30, context=context) as smtp:
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                if user:
                    smtp.login(user, password)
                smtp.send_message(msg)
    except smtplib.SMTPException as e:
        return f'Error: SMTP failed: {e!s}'
    except OSError as e:
        return f'Error: connection failed: {e!s}'

    return f'Email sent successfully to {to}.'


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient using the configured SMTP server.

    Use when the user asks to notify someone by email, send a message, or deliver
    text to an address. Requires SMTP_* environment variables to be set.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain-text body.

    Returns:
        A short status string indicating success or the error reason.
    """
    return send_email_smtp(to=to, subject=subject, body=body)


EMAIL_TOOLS = [send_email]
