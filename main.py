"""Entry point kept at the project root for convenience.

Run the app with:
    uvicorn main:app --reload
"""

from app.main import app

__all__ = ["app"]
