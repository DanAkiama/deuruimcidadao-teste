"""
Configuração do Banco de Dados

Configurações e inicialização das extensões do Flask relacionadas ao banco de dados.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

# Instâncias das extensões
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def init_database(app):
    """
    Inicializa as extensões do banco de dados com a aplicação Flask.
    
    Args:
        app: Instância da aplicação Flask
    """
    # Configuração do banco de dados
    database_url = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    
    # Inicialização das extensões
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)


def create_tables(app):
    """
    Cria as tabelas do banco de dados.
    
    Args:
        app: Instância da aplicação Flask
    """
    with app.app_context():
        db.create_all()


def drop_tables(app):
    """
    Remove todas as tabelas do banco de dados.
    
    Args:
        app: Instância da aplicação Flask
    """
    with app.app_context():
        db.drop_all()

