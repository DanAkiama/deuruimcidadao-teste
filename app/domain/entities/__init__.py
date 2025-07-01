"""
Entidades do Domínio

Entidades são objetos que possuem identidade única e representam
conceitos centrais do negócio. Elas contêm as regras de negócio
mais importantes da aplicação.
"""

from .user import User
from .complaint import Complaint
from .notification import Notification

__all__ = ['User', 'Complaint', 'Notification']

