"""
Comprehensive Logging Configuration for Tax Agent System
=========================================================

This module sets up centralized logging for the entire tax workflow system.
Logs are written to both file (logs/tax_app.log) and console.

Features:
- File logging with rotation (10MB max, keeps 7 files)
- Console logging for development/debugging
- Consistent format: [TIMESTAMP] [LEVEL] [MODULE.FUNCTION] Message
- Detailed logging level control per module
- Fast tail functionality for UI log viewers

Usage:
    from agent.logging_config import get_logger, setup_logging, tail_log_file

    # Initialize logging system (call once at app startup)
    setup_logging()

    # Get logger for a module
    logger = get_logger(__name__)
    logger.info("Something happened")
    logger.error("Something went wrong")

    # Retrieve recent logs for UI display
    recent_logs = tail_log_file(lines=50)
"""

import logging
import logging.handlers
from pathlib import Path
import os
from datetime import datetime
from typing import List, Tuple
import sys


# Configure log directory - ABSOLUTE PATH
# Path: pjj-tax-legal/logs/
_script_dir = Path(__file__).parent  # src/pjj_tax_legal/agent/
_project_root = _script_dir.parent.parent.parent  # pjj-tax-legal/
LOG_DIR = _project_root / "logs"
LOG_FILE = LOG_DIR / "tax_app.log"

# Log format: [TIMESTAMP] [LEVEL] [MODULE.FUNCTION] Message
LOG_FORMAT = logging.Formatter(
    fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s.%(funcName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up comprehensive logging system for the application.

    Args:
        level: Logging level (default: logging.INFO)

    This function:
    - Creates log directory if it doesn't exist
    - Sets up file handler with rotation (10MB max, keep 7 backups)
    - Sets up console handler for terminal output
    - Configures root logger to capture all module logs
    """
    # Create log directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # =====================================================================
    # FILE HANDLER: Rotating file logger
    # =====================================================================
    file_handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=7,  # Keep 7 backup files (70MB total)
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # File captures everything
    file_handler.setFormatter(LOG_FORMAT)
    root_logger.addHandler(file_handler)

    # =====================================================================
    # CONSOLE HANDLER: Console output for development
    # =====================================================================
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(LOG_FORMAT)
    root_logger.addHandler(console_handler)

    # =====================================================================
    # MODULE-SPECIFIC CONFIGURATION
    # =====================================================================
    # Set verbose logging for tax agents
    tax_agents_modules = [
        'orchestrator.tax_workflow.tax_planner_agent',
        'orchestrator.tax_workflow.tax_searcher_agent',
        'orchestrator.tax_workflow.tax_recommender_agent',
        'orchestrator.tax_workflow.tax_compiler_agent',
        # tax_verifier_agent removed - human does manual verification
        'orchestrator.tax_workflow.tax_tracker_agent',
        'orchestrator.tax_workflow.tax_orchestrator',
        'agent',
    ]

    for module in tax_agents_modules:
        logging.getLogger(module).setLevel(logging.DEBUG)

    # Log initialization message
    root_logger.info("=" * 80)
    root_logger.info("Logging System Initialized")
    root_logger.info(f"Log file: {LOG_FILE}")
    root_logger.info(f"Log level: {logging.getLevelName(level)}")
    root_logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (typically __name__ from caller)

    Returns:
        Logger instance configured for that module
    """
    return logging.getLogger(name)


def tail_log_file(lines: int = 50) -> List[str]:
    """
    Get the last N lines from the log file.

    Used by the Streamlit UI to display live logs in the sidebar.

    Args:
        lines: Number of recent lines to retrieve

    Returns:
        List of log line strings, most recent last
    """
    if not LOG_FILE.exists():
        return []

    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            # Read all lines
            all_lines = f.readlines()

            # Get last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            # Strip newlines and return
            return [line.rstrip('\n') for line in recent_lines]
    except Exception as e:
        return [f"Error reading logs: {str(e)}"]


def get_log_file_path() -> Path:
    """Get the path to the current log file."""
    return LOG_FILE


def clear_logs() -> None:
    """Clear the log file (useful for testing/resetting)."""
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    get_logger(__name__).info("Log file cleared")


def get_log_statistics() -> dict:
    """Get statistics about the log file."""
    if not LOG_FILE.exists():
        return {"exists": False, "size_bytes": 0, "size_mb": 0}

    size_bytes = LOG_FILE.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    return {
        "exists": True,
        "path": str(LOG_FILE),
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
        "modified": datetime.fromtimestamp(LOG_FILE.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }


# ========================================================================
# UTILITY FUNCTIONS FOR COMMON LOGGING PATTERNS
# ========================================================================

def log_agent_call(
    logger: logging.Logger,
    agent_name: str,
    method_name: str,
    input_data: dict,
) -> None:
    """Log the start of an agent method call."""
    logger.info(f"[{agent_name}.{method_name}] STARTING with input: {input_data}")


def log_agent_response(
    logger: logging.Logger,
    agent_name: str,
    method_name: str,
    output_data: dict,
    duration_ms: float = None,
) -> None:
    """Log the completion of an agent method call."""
    duration_str = f" (took {duration_ms:.1f}ms)" if duration_ms else ""
    logger.info(
        f"[{agent_name}.{method_name}] COMPLETED{duration_str} with output: {output_data}"
    )


def log_agent_error(
    logger: logging.Logger,
    agent_name: str,
    method_name: str,
    error: Exception,
) -> None:
    """Log an error from an agent method call."""
    logger.error(
        f"[{agent_name}.{method_name}] ERROR: {str(error)}",
        exc_info=True
    )


def log_search_query(
    logger: logging.Logger,
    agent_name: str,
    query: str,
    segments: list,
    constraints: dict = None,
) -> None:
    """Log a search operation."""
    constraint_str = f" with constraints: {constraints}" if constraints else ""
    logger.info(
        f"[{agent_name}] SEARCH: query='{query}' segments={segments}{constraint_str}"
    )


def log_search_results(
    logger: logging.Logger,
    agent_name: str,
    total_found: int,
    results_preview: list,
) -> None:
    """Log search results."""
    logger.info(
        f"[{agent_name}] SEARCH_RESULTS: found {total_found} matches, "
        f"returning top {len(results_preview)}"
    )


def log_json_parsing(
    logger: logging.Logger,
    agent_name: str,
    json_string: str,
    parsed_data: dict,
) -> None:
    """Log JSON parsing operation."""
    logger.debug(
        f"[{agent_name}] PARSED_JSON: input='{json_string[:100]}...' -> {parsed_data}"
    )


if __name__ == "__main__":
    # Test the logging system
    setup_logging()
    logger = get_logger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print("\nLog file location:", get_log_file_path())
    print("Log statistics:", get_log_statistics())
    print("\nRecent logs:")
    for line in tail_log_file(10):
        print(f"  {line}")
