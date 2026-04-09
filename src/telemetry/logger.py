import json
import logging
import os
from datetime import UTC, datetime


class IndustryLogger:
    """JSON lines to console and a daily file under ``logs/``."""

    def __init__(self, name: str = 'AI-Lab-Agent', log_dir: str = 'logs') -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler (JSON)
        log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
        file_handler = logging.FileHandler(log_file)

        # Console Handler
        console_handler = logging.StreamHandler()

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_event(self, event_type: str, data: dict[str, object]) -> None:
        """Emit one structured event."""
        payload = {
            'timestamp': datetime.now(UTC).isoformat(),
            'event': event_type,
            'data': data,
        }
        self.logger.info(json.dumps(payload))

    def info(self, msg: str) -> None:
        self.logger.info(msg)

    def error(self, msg: str, exc_info: bool = True) -> None:
        self.logger.error(msg, exc_info=exc_info)


# Global logger instance
logger = IndustryLogger()
