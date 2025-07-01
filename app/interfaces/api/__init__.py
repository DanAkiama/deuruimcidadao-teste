"""
API Interface - Interface da API REST

Contém as rotas e controllers da API REST da aplicação.
"""

from .auth_routes import auth_bp
from .complaint_routes import complaint_bp
from .user_routes import user_bp
from .notification_routes import notification_bp

__all__ = ['auth_bp', 'complaint_bp', 'user_bp', 'notification_bp']

