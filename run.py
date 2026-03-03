# @Version :1.0
# @Author  : Mingyue
# @File    : run.py.py
# @Time    : 02/03/2026 20:33
"""
Entry point for the AI Coding Assistant Flask application.
Run with:  python run.py
"""
import sys
import os

# Ensure app package is on the path
sys.path.insert(0, os.path.dirname(__file__))

from app.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀  AI Coding Assistant running at http://localhost:{port}\n")
    app.run(debug=True, host="0.0.0.0", port=port)