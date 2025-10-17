#!/usr/bin/env python3
"""
Local development server for OdontoLab API.
"""

if __name__ == "__main__":
    import uvicorn
    
    # Run the development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )