"""
Settings and Configuration for Agent Module
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini AI configuration (primary backend)
# GEMINI_API_KEY is no longer needed with Vertex AI authentication
GEMINI_MODEL = "gemini-pro-latest"

# No longer needed with Vertex AI authentication

# Agent settings
MAX_TOOL_TURNS = 20

# Memory
MEMORY_PATH = "memory_dir"
FILE_SIZE_LIMIT = 1024 * 1024  # 1MB
DIR_SIZE_LIMIT = 1024 * 1024 * 10  # 10MB
MEMORY_SIZE_LIMIT = 1024 * 1024 * 100  # 100MB

# Engine
SANDBOX_TIMEOUT = 20

# Path settings
SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent / "system_prompt.txt"
SAVE_CONVERSATION_PATH = Path("output") / "conversations"
