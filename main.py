"""
Entry Point
===========

This script serves as the entry point for the application.
It uses Uvicorn to run the FastAPI app defined in `app.app`.
"""

import uvicorn
import os

if __name__ == "__main__":
    # Get port from environment variable (standard for Render) or default to 10000
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.app:app", host="0.0.0.0", port=port, reload=False)
