from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from src.database import db
from src.models.user import User
from src.models.notification import Notification
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validação de campos obrigatórios
        required_fields = ['username', 'email', 'cpf', 'password', 'full_name', 'city']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Campo {field} é obrigatório'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        cpf = data.get('cpf').strip()
        password = data.get('password')
        full_name = data.get('full_name').strip()
        city = data.get('city').strip().lower()
        role = data.get('role', 'reclamante')
        phone = data.get('phone', '').strip() if data.get('phone') else None
        
        # Validações
        if len(username) < 3:
            return jsonify({'message': 'Nome de usuário deve ter pelo menos 3 caracteres'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Senha deve ter pelo menos 6 caracteres'}), 400
        
        if not User.validate_email(email):
            return jsonify({'message': 'Email inválido'}), 400
        
        if not User.validate_cpf(cpf):
            return jsonify({'message': 'CPF inválido'}), 400
        
        if role not in ['reclamante', 'responsavel']:
            return jsonify({'message': 'Tipo de usuário inválido'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Nome de usuário já existe'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email já cadastrado'}), 409
        
        if User.query.filter_by(cpf=User.format_cpf(cpf)).first():
            return jsonify({'message': 'CPF já cadastrado'}), 409
        
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email,
            cpf=cpf,
            password=password,
            role=role,
            city=city,
            full_name=full_name,
            phone=phone
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Criar notificação de boas-vindas
        welcome_message = f"Bem-vindo(a) ao deuruim{city}, {full_name}! Sua conta foi criada com sucesso."
        Notification.create_notification(
            user_id=new_user.id,
            type='welcome',
            title='Bem-vindo!',
            message=welcome_message
        )
        
        # Gerar tokens
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro no registro: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('login') or not data.get('password'):
            return jsonify({'message': 'Login e senha são obrigatórios'}), 400
        
        login_field = data.get('login').strip()
        password = data.get('password')
        
        # Buscar usuário por username, email ou CPF
        user = None
        if '@' in login_field:
            user = User.query.filter_by(email=login_field.lower()).first()
        elif '.' in login_field and '-' in login_field:  # Formato de CPF
            user = User.query.filter_by(cpf=login_field).first()
        else:
            user = User.query.filter_by(username=login_field).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Conta desativada'}), 401
        
        # Gerar tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Usuário não encontrado ou inativo'}), 404
        
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no refresh: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/validate-field', methods=['POST'])
def validate_field():
    """Endpoint para validar campos em tempo real durante o registro"""
    try:
        data = request.get_json()
        field = data.get('field')
        value = data.get('value', '').strip()
        
        if field == 'username':
            if len(value) < 3:
                return jsonify({'valid': False, 'message': 'Nome de usuário deve ter pelo menos 3 caracteres'}), 200
            if User.query.filter_by(username=value).first():
                return jsonify({'valid': False, 'message': 'Nome de usuário já existe'}), 200
            return jsonify({'valid': True}), 200
            
        elif field == 'email':
            if not User.validate_email(value):
                return jsonify({'valid': False, 'message': 'Email inválido'}), 200
            if User.query.filter_by(email=value.lower()).first():
                return jsonify({'valid': False, 'message': 'Email já cadastrado'}), 200
            return jsonify({'valid': True}), 200
            
        elif field == 'cpf':
            if not User.validate_cpf(value):
                return jsonify({'valid': False, 'message': 'CPF inválido'}), 200
            if User.query.filter_by(cpf=User.format_cpf(value)).first():
                return jsonify({'valid': False, 'message': 'CPF já cadastrado'}), 200
            return jsonify({'valid': True}), 200
        
        return jsonify({'valid': False, 'message': 'Campo não reconhecido'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro na validação: {str(e)}")
        return jsonify({'valid': False, 'message': 'Erro interno do servidor'}), 500

