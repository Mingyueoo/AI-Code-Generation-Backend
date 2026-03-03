# @Version :1.0
# @Author  : Mingyue
# @File    : __init__.py.py
# @Time    : 02/03/2026 19:55
from app.routes.api import api_bp
from app.routes.web import web_bp

__all__ = ["api_bp", "web_bp"]