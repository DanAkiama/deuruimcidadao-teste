"""
Rotas de Notificações

Contém as rotas da API relacionadas às notificações.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...usecases.notification_usecases import (
    GetUserNotificationsUseCase,
    MarkNotificationAsReadUseCase,
    GetUnreadNotificationsCountUseCase
)

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notification_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Endpoint para obter notificações do usuário."""
    try:
        user_id = get_jwt_identity()
        
        # Obter filtros da query string
        filters = {}
        
        if request.args.get('is_read'):
            filters['is_read'] = request.args.get('is_read').lower() == 'true'
        
        if request.args.get('notification_type'):
            filters['notification_type'] = request.args.get('notification_type')
        
        if request.args.get('channel'):
            filters['channel'] = request.args.get('channel')
        
        # Executar caso de uso
        use_case = GetUserNotificationsUseCase()
        success, message, notifications_data = use_case.execute(user_id, filters)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': notifications_data
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


@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_as_read(notification_id):
    """Endpoint para marcar notificação como lida."""
    try:
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = MarkNotificationAsReadUseCase()
        success, message = use_case.execute(user_id, notification_id)
        
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


@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Endpoint para obter contagem de notificações não lidas."""
    try:
        user_id = get_jwt_identity()
        
        # Executar caso de uso
        use_case = GetUnreadNotificationsCountUseCase()
        success, message, count = use_case.execute(user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'data': {'unread_count': count}
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


@notification_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_as_read():
    """Endpoint para marcar todas as notificações como lidas."""
    try:
        user_id = get_jwt_identity()
        
        # Buscar todas as notificações não lidas
        get_use_case = GetUserNotificationsUseCase()
        success, message, notifications = get_use_case.execute(user_id, {'is_read': False})
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Marcar cada uma como lida
        mark_use_case = MarkNotificationAsReadUseCase()
        marked_count = 0
        
        for notification in notifications:
            success, _ = mark_use_case.execute(user_id, notification['id'])
            if success:
                marked_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{marked_count} notificações marcadas como lidas',
            'data': {'marked_count': marked_count}
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

