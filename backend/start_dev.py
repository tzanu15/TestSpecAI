#!/usr/bin/env python3
"""
Development server startup script for TestSpecAI backend.
"""

import uvicorn
import os
import sys

def main():
    """Start the development server."""
    print("🚀 Starting TestSpecAI Backend Development Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)

    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
