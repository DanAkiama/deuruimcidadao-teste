"""
Arquivo Principal da Aplicação

Configura e inicializa a aplicação Flask seguindo Clean Architecture.
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from .infrastructure.db.database import init_database, create_tables
from .interfaces.api import auth_bp, complaint_bp, user_bp, notification_bp

# Carregar variáveis de ambiente
load_dotenv()


def create_app():
    """
    Factory function para criar a aplicação Flask.
    
    Returns:
        Instância configurada da aplicação Flask
    """
    app = Flask(__name__, static_folder='../src/static')
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Configurações de upload
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Configurar CORS
    CORS(app, origins="*")
    
    # Inicializar banco de dados
    init_database(app)
    
    # Registrar blueprints da API
    app.register_blueprint(auth_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(notification_bp)
    
    # Rotas para servir arquivos estáticos
    @app.route('/')
    def index():
        """Serve a página principal."""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        """Serve arquivos estáticos."""
        return send_from_directory(app.static_folder, filename)
    
    @app.route('/uploads/<path:filename>')
    def uploaded_files(filename):
        """Serve arquivos de upload."""
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        create_tables(app)
    
    return app


def main():
    """Função principal para executar a aplicação."""
    app = create_app()
    
    # Configurações do servidor
    host = '0.0.0.0'
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando deuruimcidadao em http://{host}:{port}")
    print(f"📁 Pasta estática: {app.static_folder}")
    print(f"🔧 Modo debug: {debug}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()

