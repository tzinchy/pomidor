import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
import sys


class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = logging.getLogger("app")
        self.logger.setLevel(logging.INFO)

        # Очищаем существующие обработчики
        if self.logger.handlers:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

        # Создаем папку для логов
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Форматтер
        formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

        # Файловый обработчик
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def query(self, query: str, params: Optional[Dict[str, Any]] = None):
        message = f"SQL: {query}"
        if params:
            message += f"\n└── PARAMS: {params}"
        self.logger.info(message)

    def error(self, error: Exception, context: Optional[str] = None):
        error_msg = f"ERROR: {str(error)}"
        if context:
            error_msg += f" | CONTEXT: {context}"
        self.logger.error(error_msg, exc_info=True)

    def info(self, message: str):
        self.logger.info(message)


logger = AppLogger()
