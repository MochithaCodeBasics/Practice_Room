import logging
import json
import os
from datetime import datetime
from pathlib import Path
from fastapi import Request
from typing import Optional

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
AUDIT_LOG_FILE = LOGS_DIR / "audit.log"

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# File handler for audit logs
file_handler = logging.FileHandler(AUDIT_LOG_FILE)
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
audit_logger.addHandler(file_handler)

def log_audit_event(
    action: str,
    user: Optional[str] = None,
    ip: Optional[str] = None,
    status: str = "success",
    details: Optional[dict] = None,
    request: Optional[Request] = None
):
    """
    Log a structured audit event.
    
    Args:
        action: The action being performed (e.g., "login", "create_question")
        user: The username or ID of the user performing the action
        ip: The client's IP address
        status: "success", "failure", or "error"
        details: Additional context for the event
        request: FastAPI Request object to automatically extract IP and user context
    """
    timestamp = datetime.utcnow().isoformat()
    
    # Extract IP and user from request if provided
    current_ip = ip
    if request:
        current_ip = request.client.host if request.client else "unknown"
        # If user not provided, we might try to extract from state if we reach that far
        if not user and hasattr(request.state, "user"):
            user = request.state.user.username if hasattr(request.state.user, "username") else str(request.state.user)

    event = {
        "timestamp": timestamp,
        "action": action,
        "user": user or "anonymous",
        "ip": current_ip or "unknown",
        "status": status,
        "details": details or {}
    }
    
    audit_logger.info(json.dumps(event))

# Also provide a standard utility for error logging if needed
error_logger = logging.getLogger("errors")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler(LOGS_DIR / "error.log")
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)
