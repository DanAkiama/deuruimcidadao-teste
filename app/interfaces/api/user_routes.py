"""
Rotas de Usuário

Contém as rotas da API relacionadas ao perfil e gerenciamento de usuários.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...usecases.user_usecases import (
    UpdateUserProfileUseCase,
    ChangePasswordUseCase,
    GetUserProfileUseCase,
    UploadProfilePictureUseCase
)

user_bp = Blueprint('users', __name__, url_prefix='/api/users')


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Endpoint para obter perfil do usuário atual."""
    try:
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


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Endpoint para atualizar perfil do usuário."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Executar caso de uso
        use_case = UpdateUserProfileUseCase()
        success, message, user_data = use_case.execute(user_id, data)
        
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
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@user_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Endpoint para alterar senha do usuário."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Validar confirmação de senha
        if 'confirm_password' in data:
            if data['new_password'] != data['confirm_password']:
                return jsonify({
                    'success': False,
                    'message': 'Nova senha e confirmação não coincidem'
                }), 400
        
        # Executar caso de uso
        use_case = ChangePasswordUseCase()
        success, message = use_case.execute(user_id, data)
        
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


@user_bp.route('/upload-avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """Endpoint para upload de foto de perfil."""
    try:
        user_id = get_jwt_identity()
        
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo selecionado'
            }), 400
        
        # Validar tipo de arquivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'success': False,
                'message': 'Tipo de arquivo não permitido'
            }), 400
        
        # Salvar arquivo (implementação simplificada)
        import os
        from werkzeug.utils import secure_filename
        
        upload_folder = 'uploads/profiles'
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(f"user_{user_id}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Executar caso de uso
        use_case = UploadProfilePictureUseCase()
        success, message, saved_path = use_case.execute(user_id, file_path)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': {'file_path': saved_path}
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


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_public_profile(user_id):
    """Endpoint para obter perfil público de um usuário."""
    try:
        # Executar caso de uso
        use_case = GetUserProfileUseCase()
        success, message, user_data = use_case.execute(user_id)
        
        if success:
            # Remover informações sensíveis para perfil público
            public_data = {
                'id': user_data['id'],
                'username': user_data['username'],
                'full_name': user_data['full_name'],
                'city': user_data['city'],
                'profile_picture': user_data['profile_picture'],
                'bio': user_data['bio'],
                'created_at': user_data['created_at'],
                'statistics': user_data.get('statistics', {})
            }
            
            return jsonify({
                'success': True,
                'message': message,
                'data': public_data
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


@user_bp.route('/cities', methods=['GET'])
def get_cities():
    """Endpoint para obter cidades disponíveis."""
    try:
        cities = [
            {'value': 'cuiaba', 'label': 'Cuiabá - MT'},
            {'value': 'varzea_grande', 'label': 'Várzea Grande - MT'}
        ]
        
        return jsonify({
            'success': True,
            'message': 'Cidades encontradas',
            'data': cities
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

