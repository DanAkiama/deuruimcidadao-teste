import os
import sys
from datetime import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.database import db, bcrypt, jwt
from src.models.user import User
from src.models.complaint import Complaint, Vote, Response
from src.models.notification import Notification
from src.models.gamification import UserPoints, UserBadge, Badge, PointHistory, CityRanking

# Importar blueprints
from src.routes.auth import auth_bp
from src.routes.complaints import complaints_bp
from src.routes.user_profile import profile_bp
from src.routes.admin import admin_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = 'deuruimcidadao_secret_key_2024'
app.config['JWT_SECRET_KEY'] = 'deuruimcidadao_jwt_secret_2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de upload
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Inicializar extensões
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(complaints_bp, url_prefix='/api')
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

# Importar e registrar novos blueprints
from src.routes.notifications import notifications_bp
from src.routes.maps import maps_bp

app.register_blueprint(notifications_bp)
app.register_blueprint(maps_bp)

# Criar tabelas e dados iniciais
with app.app_context():
    db.create_all()
    
    # Inicializar serviços
    from src.services.notification_service import notification_service
    from src.services.maps_service import maps_service
    
    notification_service.init_app(app)
    maps_service.init_app(app)
    
    # Criar badges padrão se não existirem
    default_badges = [
        {
            'name': 'Primeiro Passo',
            'description': 'Fez sua primeira reclamação',
            'icon': 'star',
            'category': 'activity'
        },
        {
            'name': 'Cidadão Iniciante',
            'description': 'Alcançou nível 5',
            'icon': 'star',
            'category': 'level',
            'requirement': 5
        },
        {
            'name': 'Cidadão Ativo',
            'description': 'Alcançou nível 10',
            'icon': 'star-fill',
            'category': 'level',
            'requirement': 10
        },
        {
            'name': 'Cidadão Engajado',
            'description': 'Alcançou nível 25',
            'icon': 'award',
            'category': 'level',
            'requirement': 25
        },
        {
            'name': 'Cidadão Exemplar',
            'description': 'Alcançou nível 50',
            'icon': 'trophy',
            'category': 'level',
            'requirement': 50
        },
        {
            'name': 'Guardião da Cidade',
            'description': 'Alcançou nível 100',
            'icon': 'crown',
            'category': 'level',
            'requirement': 100
        },
        {
            'name': 'Colaborador',
            'description': 'Votou em 10 reclamações',
            'icon': 'hand-thumbs-up',
            'category': 'activity',
            'requirement': 10
        },
        {
            'name': 'Engajado',
            'description': 'Fez 5 reclamações',
            'icon': 'chat-dots',
            'category': 'activity',
            'requirement': 5
        },
        {
            'name': 'Persistente',
            'description': 'Teve 3 reclamações resolvidas',
            'icon': 'check-circle',
            'category': 'activity',
            'requirement': 3
        }
    ]
    
    for badge_data in default_badges:
        existing_badge = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing_badge:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar badges padrão: {e}")

# Rotas para servir arquivos estáticos e SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Rota para servir uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(app.static_folder, 'uploads')
    return send_from_directory(upload_folder, filename)

# Handlers de erro JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'message': 'Token expirado'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'message': 'Token inválido'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'message': 'Token de acesso necessário'}, 401

# Rota de health check
@app.route('/api/health')
def health_check():
    return {'status': 'ok', 'message': 'deuruimcidadao API está funcionando'}, 200

# Rota para informações da API
@app.route('/api/info')
def api_info():
    return {
        'name': 'deuruimcidadao API',
        'version': '1.0.0',
        'description': 'API para sistema de reclamações urbanas multi-cidade',
        'features': [
            'Autenticação JWT',
            'Sistema de reclamações',
            'Gamificação',
            'Painel administrativo',
            'Notificações',
            'Sistema de votação',
            'Upload de mídia',
            'Geolocalização',
            'Relatórios'
        ]
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

