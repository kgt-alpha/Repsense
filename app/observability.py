"""Optional, privacy-conscious tracing for RepSense operations."""
from contextlib import contextmanager
from typing import Iterator

from app.config import get_settings


@contextmanager
def trace_operation(name: str) -> Iterator[None]:
    """Trace an operation when Langfuse is configured; otherwise act as a no-op.

    User content, workout values, credentials, and request bodies are never sent
    as trace metadata by this helper.
    """
    settings = get_settings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        yield
        return
    try:
        from langfuse import get_client

        client = get_client()
        with client.start_as_current_span(name=name):
            yield
    except ImportError:
        yield
