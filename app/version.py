"""Single source of truth for the project version.

Referenced by the FastAPI app, pyproject.toml (kept in sync manually — a CI
check compares them) and the release pipeline.
"""

__version__ = "1.2.0"
