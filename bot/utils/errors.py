import logging as log
from typing import Any

from aiogram.handlers import ErrorHandler


class ErrorsLogger(ErrorHandler):
    """Helps logging errors"""
    async def handle(self) -> Any:
        log.exception(
            "Cause unexpected exception %s: %s",
            self.exception_name,
            self.exception_message
        )