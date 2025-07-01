from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.notification_service import notification_service
from src.database import db
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications with pagination"""
    try:
        user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        offset = (page - 1) * per_page
        
        # Get notifications
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            limit=per_page,
            offset=offset
        )
        
        # Get unread count
        unread_count = notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count,
            'page': page,
            'per_page': per_page,
            'has_more': len(notifications) == per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar notificações'
        }), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        user_id = get_jwt_identity()
        
        success = notification_service.mark_notification_as_read(
            notification_id=notification_id,
            user_id=user_id
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notificação marcada como lida'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Notificação não encontrada'
            }), 404
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao marcar notificação como lida'
        }), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    """Mark all notifications as read for user"""
    try:
        user_id = get_jwt_identity()
        
        from src.models.notification import Notification
        from datetime import datetime
        
        # Update all unread notifications
        Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Todas as notificações foram marcadas como lidas'
        }), 200
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro ao marcar notificações como lidas'
        }), 500

@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get count of unread notifications"""
    try:
        user_id = get_jwt_identity()
        
        unread_count = notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar contagem de notificações'
        }), 500

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get user notification preferences"""
    try:
        user_id = get_jwt_identity()
        
        from src.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'preferences': {
                'email_notifications': user.email_notifications,
                'whatsapp_notifications': user.whatsapp_notifications,
                'push_notifications': user.push_notifications
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar preferências de notificação'
        }), 500

@notifications_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """Update user notification preferences"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        from src.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404
        
        # Update preferences
        if 'email_notifications' in data:
            user.email_notifications = bool(data['email_notifications'])
        
        if 'whatsapp_notifications' in data:
            user.whatsapp_notifications = bool(data['whatsapp_notifications'])
        
        if 'push_notifications' in data:
            user.push_notifications = bool(data['push_notifications'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferências atualizadas com sucesso',
            'preferences': {
                'email_notifications': user.email_notifications,
                'whatsapp_notifications': user.whatsapp_notifications,
                'push_notifications': user.push_notifications
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Erro ao atualizar preferências'
        }), 500

@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def send_test_notification():
    """Send test notification (for development/testing)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        notification_type = data.get('type', 'welcome')
        extra_data = data.get('extra_data', {})
        
        success = notification_service.send_system_notification(
            user_id=user_id,
            notification_type=notification_type,
            extra_data=extra_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notificação de teste enviada com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao enviar notificação de teste'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao enviar notificação de teste'
        }), 500

# Admin routes for bulk notifications
@notifications_bp.route('/admin/send-bulk', methods=['POST'])
@jwt_required()
def send_bulk_notification():
    """Send bulk notification to multiple users (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is admin
        from src.models.user import User
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'gestor_publico':
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        
        user_ids = data.get('user_ids', [])
        notification_type = data.get('type', 'system_announcement')
        extra_data = data.get('extra_data', {})
        
        if not user_ids:
            return jsonify({
                'success': False,
                'message': 'Lista de usuários é obrigatória'
            }), 400
        
        results = notification_service.send_bulk_notifications(
            user_ids=user_ids,
            notification_type=notification_type,
            extra_data=extra_data
        )
        
        return jsonify({
            'success': True,
            'message': f'Notificações enviadas: {results["sent"]} sucesso, {results["failed"]} falhas',
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error sending bulk notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao enviar notificações em lote'
        }), 500

@notifications_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """Get notification statistics (admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if user is admin
        from src.models.user import User
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'gestor_publico':
            return jsonify({
                'success': False,
                'message': 'Acesso negado'
            }), 403
        
        from src.models.notification import Notification
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Get stats for last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Total notifications
        total_notifications = Notification.query.filter(
            Notification.created_at >= thirty_days_ago
        ).count()
        
        # Email success rate
        email_sent = Notification.query.filter(
            Notification.created_at >= thirty_days_ago,
            Notification.email_sent == True
        ).count()
        
        # WhatsApp success rate
        whatsapp_sent = Notification.query.filter(
            Notification.created_at >= thirty_days_ago,
            Notification.whatsapp_sent == True
        ).count()
        
        # Notifications by type
        type_stats = db.session.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).filter(
            Notification.created_at >= thirty_days_ago
        ).group_by(Notification.type).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_notifications': total_notifications,
                'email_sent': email_sent,
                'whatsapp_sent': whatsapp_sent,
                'email_success_rate': round((email_sent / max(total_notifications, 1)) * 100, 2),
                'whatsapp_success_rate': round((whatsapp_sent / max(total_notifications, 1)) * 100, 2),
                'by_type': [{'type': t.type, 'count': t.count} for t in type_stats]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao buscar estatísticas de notificações'
        }), 500

