"""Agent-facing tools (database stubs, email, …)."""

from .email import EMAIL_TOOLS, send_email

__all__ = ['EMAIL_TOOLS', 'send_email']
