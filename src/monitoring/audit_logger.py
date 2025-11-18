"""Audit logging for compliance."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from src.utils.logger import LoggerMixin
from src.config.settings import get_settings


class AuditLogger(LoggerMixin):
    """Log trading activities for audit trail."""

    def __init__(self):
        """Initialize audit logger."""
        self.settings = get_settings()
        self.audit_path = Path(self.settings.log_path) / "audit"
        self.audit_path.mkdir(parents=True, exist_ok=True)

    def log_prediction(self, symbol: str, prediction: Dict[str, Any]) -> None:
        """Log a prediction."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "prediction",
            "symbol": symbol,
            "data": prediction,
        }
        self._write_audit_log(entry)

    def log_signal(self, symbol: str, signal: Dict[str, Any]) -> None:
        """Log a trading signal."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "signal",
            "symbol": symbol,
            "data": signal,
        }
        self._write_audit_log(entry)

    def log_trade(self, symbol: str, trade: Dict[str, Any]) -> None:
        """Log a trade execution."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "trade",
            "symbol": symbol,
            "data": trade,
        }
        self._write_audit_log(entry)

    def _write_audit_log(self, entry: Dict[str, Any]) -> None:
        """Write audit log entry to file."""
        log_file = self.audit_path / f"audit_{datetime.now():%Y%m%d}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
