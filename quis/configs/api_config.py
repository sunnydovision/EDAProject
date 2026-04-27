"""
OpenAI API configuration.

OPENAI_USE_RESPONSES_API:
- True: Use OpenAI Responses API (for models like gpt-5, o1, gpt-5-nano)
  - Different response format with reasoning models
  - Uses client.responses.create() instead of chat.completions.create()
- False: Use Chat Completions API (for models like gpt-4o-mini, gpt-4)
  - Traditional chat format
"""

import os


# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", None)  # e.g. "https://.../v1" for local/vendor endpoints

# API type selection
USE_RESPONSES_API = os.getenv("OPENAI_USE_RESPONSES_API", "1").strip().lower() in ("1", "true", "yes")

# Token usage logging
IFQ_USAGE_OUTPUT = os.getenv("IFQ_USAGE_OUTPUT", "").strip()


def get_default_model() -> str:
    """Get default model based on API type."""
    if USE_RESPONSES_API:
        return "gpt-5.4"
    else:
        return "gpt-4o-mini"
