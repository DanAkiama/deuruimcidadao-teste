"""
Rotas de Autenticação

Contém as rotas da API relacionadas à autenticação de usuários.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...usecases.auth_usecases import (
    RegisterUserUseCase, 
    LoginUserUseCase, 
    LogoutUserUseCase,
    CheckUsernameAvailabilityUseCase,
    CheckEmailAvailabilityUseCase
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novos usuários."""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['username', 'email', 'cpf', 'password', 'full_name', 'city']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Validar confirmação de senha
        if 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                return jsonify({
                    'success': False,
                    'message': 'Senhas não coincidem'
                }), 400
        
        # Executar caso de uso
        use_case = RegisterUserUseCase()
        success, message, user_data = use_case.execute(data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários."""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        if 'login_field' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Login field e password são obrigatórios'
            }), 400
        
        # Executar caso de uso
        use_case = LoginUserUseCase()
        success, message, response_data = use_case.execute(data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': response_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint para logout de usuários."""
    try:
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = LogoutUserUseCase()
        success, message = use_case.execute(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@auth_bp.route('/check-username', methods=['GET'])
def check_username():
    """Endpoint para verificar disponibilidade de username."""
    try:
        username = request.args.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username é obrigatório'
            }), 400
        
        # Executar caso de uso
        use_case = CheckUsernameAvailabilityUseCase()
        available, message = use_case.execute(username)
        
        return jsonify({
            'success': True,
            'available': available,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@auth_bp.route('/check-email', methods=['GET'])
def check_email():
    """Endpoint para verificar disponibilidade de email."""
    try:
        email = request.args.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email é obrigatório'
            }), 400
        
        # Executar caso de uso
        use_case = CheckEmailAvailabilityUseCase()
        available, message = use_case.execute(email)
        
        return jsonify({
            'success': True,
            'available': available,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Endpoint para obter dados do usuário atual."""
    try:
        from ...usecases.user_usecases import GetUserProfileUseCase
        
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = GetUserProfileUseCase()
        success, message, user_data = use_case.execute(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': user_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

