"""
JSON-lines structured logging utility.
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class JSONLogger:
    """Structured logger that outputs JSON lines."""
    
    def __init__(self, log_file: str, service_name: str):
        self.log_file = Path(log_file)
        self.service_name = service_name
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logger
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        
        # Console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        self.logger.addHandler(console_handler)
    
    def log_request(
        self,
        request_id: str,
        endpoint: str,
        tool: Optional[str] = None,
        status: str = "success",
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a request in JSON format."""
        log_entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "request_id": request_id,
            "endpoint": endpoint,
            "tool": tool,
            "status": status,
            "latency_ms": latency_ms,
            "error": error
        }
        
        if metadata:
            log_entry.update(metadata)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Log to Python logger
        if status == "error":
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
    
    def tail_logs(self, n: int = 200) -> list[Dict[str, Any]]:
        """Read last n lines from log file."""
        if not self.log_file.exists():
            return []
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        logs = []
        for line in lines[-n:]:
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
        
        return logs
