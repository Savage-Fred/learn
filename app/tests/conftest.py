import os

# Ensure unit tests default to deterministic mock LLM mode unless explicitly overridden
os.environ.setdefault("LEARN_USE_MOCK_LLM", "1")
