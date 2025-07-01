"""
Database Infrastructure - Infraestrutura de Banco de Dados

Contém configurações e implementações específicas do banco de dados,
incluindo modelos SQLAlchemy e repositórios.
"""

from .database import db, bcrypt
from .models import UserModel, ComplaintModel, NotificationModel, VoteModel, ResponseModel

__all__ = [
    'db', 
    'bcrypt', 
    'UserModel', 
    'ComplaintModel', 
    'NotificationModel', 
    'VoteModel', 
    'ResponseModel'
]

