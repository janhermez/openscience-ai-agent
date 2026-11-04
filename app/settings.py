import os
from dotenv import load_dotenv

load_dotenv()


def backend() -> str:
    mode = os.getenv("DATA_BACKEND", "fixture").lower()
    if mode not in {"fixture", "openalex"}:
        raise ValueError("DATA_BACKEND must be 'fixture' or 'openalex'")
    return mode
