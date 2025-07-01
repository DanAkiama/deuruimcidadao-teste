"""
Rotas de Reclamações

Contém as rotas da API relacionadas às reclamações.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...usecases.complaint_usecases import (
    CreateComplaintUseCase,
    UpdateComplaintUseCase,
    VoteComplaintUseCase,
    GetComplaintsUseCase,
    DeleteComplaintUseCase
)

complaint_bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')


@complaint_bp.route('', methods=['POST'])
@jwt_required()
def create_complaint():
    """Endpoint para criar uma nova reclamação."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Executar caso de uso
        use_case = CreateComplaintUseCase()
        success, message, complaint_data = use_case.execute(user_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': complaint_data
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


@complaint_bp.route('', methods=['GET'])
def get_complaints():
    """Endpoint para listar reclamações."""
    try:
        # Obter filtros da query string
        filters = {}
        
        if request.args.get('city'):
            filters['city'] = request.args.get('city')
        
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        
        if request.args.get('status'):
            filters['status'] = request.args.get('status')
        
        if request.args.get('user_id'):
            filters['user_id'] = int(request.args.get('user_id'))
        
        # Obter ID do usuário se autenticado (para verificar votos)
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        # Executar caso de uso
        use_case = GetComplaintsUseCase()
        success, message, complaints_data = use_case.execute(filters, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': complaints_data
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


@complaint_bp.route('/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """Endpoint para obter uma reclamação específica."""
    try:
        # Obter ID do usuário se autenticado
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        # Buscar reclamação específica
        filters = {'id': complaint_id}
        use_case = GetComplaintsUseCase()
        success, message, complaints_data = use_case.execute(filters, user_id)
        
        if success and complaints_data:
            return jsonify({
                'success': True,
                'message': message,
                'data': complaints_data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Reclamação não encontrada'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500


@complaint_bp.route('/<int:complaint_id>', methods=['PUT'])
@jwt_required()
def update_complaint(complaint_id):
    """Endpoint para atualizar uma reclamação."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Executar caso de uso
        use_case = UpdateComplaintUseCase()
        success, message, complaint_data = use_case.execute(user_id, complaint_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': complaint_data
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


@complaint_bp.route('/<int:complaint_id>', methods=['DELETE'])
@jwt_required()
def delete_complaint(complaint_id):
    """Endpoint para excluir uma reclamação."""
    try:
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = DeleteComplaintUseCase()
        success, message = use_case.execute(user_id, complaint_id)
        
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


@complaint_bp.route('/<int:complaint_id>/vote', methods=['POST'])
@jwt_required()
def vote_complaint(complaint_id):
    """Endpoint para votar em uma reclamação."""
    try:
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = VoteComplaintUseCase()
        success, message, vote_data = use_case.execute(user_id, complaint_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': vote_data
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


@complaint_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_complaints():
    """Endpoint para obter reclamações do usuário atual."""
    try:
        user_id = get_jwt_identity()
        
        # Filtrar por usuário atual
        filters = {'user_id': user_id}
        
        # Executar caso de uso
        use_case = GetComplaintsUseCase()
        success, message, complaints_data = use_case.execute(filters, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': complaints_data
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


@complaint_bp.route('/categories', methods=['GET'])
def get_categories():
    """Endpoint para obter categorias disponíveis."""
    try:
        from ...domain.entities.complaint import ComplaintCategory
        
        categories = [
            {'value': cat.value, 'label': cat.value.title()}
            for cat in ComplaintCategory
        ]
        
        return jsonify({
            'success': True,
            'message': 'Categorias encontradas',
            'data': categories
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

