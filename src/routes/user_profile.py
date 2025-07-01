from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.complaint import Complaint
from src.models.notification import Notification
from src.models.gamification import UserPoints, UserBadge, PointHistory
from sqlalchemy import func, desc
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file):
    """Salva foto de perfil e retorna o caminho"""
    if file and allowed_file(file.filename):
        # Criar diretório se não existir
        upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_path, unique_filename)
        
        # Redimensionar imagem para economizar espaço
        try:
            image = Image.open(file)
            # Redimensionar mantendo proporção (máximo 400x400)
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            image.save(file_path, optimize=True, quality=85)
            
            return f"{UPLOAD_FOLDER}/{unique_filename}"
        except Exception as e:
            current_app.logger.error(f"Erro ao processar imagem: {str(e)}")
            return None
    return None

@profile_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Buscar estatísticas do usuário
        complaints_count = Complaint.query.filter_by(user_id=current_user_id).count()
        resolved_complaints = Complaint.query.filter_by(
            user_id=current_user_id, 
            status='resolvido'
        ).count()
        
        # Buscar pontos e gamificação
        user_points = UserPoints.query.filter_by(user_id=current_user_id).first()
        if not user_points:
            user_points = UserPoints(user_id=current_user_id)
            db.session.add(user_points)
            db.session.commit()
        
        # Buscar badges
        badges = [ub.to_dict() for ub in user.user_badges]
        
        # Buscar ranking
        ranking = user.get_ranking()
        
        # Buscar histórico de pontos recente
        recent_points = PointHistory.query.filter_by(user_id=current_user_id)\
            .order_by(desc(PointHistory.created_at)).limit(10).all()
        
        profile_data = user.to_dict()
        profile_data.update({
            'statistics': {
                'complaints_count': complaints_count,
                'resolved_complaints': resolved_complaints,
                'resolution_rate': (resolved_complaints / complaints_count * 100) if complaints_count > 0 else 0
            },
            'gamification': {
                'points': user_points.to_dict(),
                'badges': badges,
                'ranking': ranking,
                'recent_activity': [rp.to_dict() for rp in recent_points]
            }
        })
        
        return jsonify({'profile': profile_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar perfil: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        if 'full_name' in data and data['full_name'].strip():
            user.full_name = data['full_name'].strip()
        
        if 'phone' in data:
            user.phone = data['phone'].strip() if data['phone'] else None
        
        if 'bio' in data:
            user.bio = data['bio'].strip() if data['bio'] else None
        
        # Validar email se fornecido
        if 'email' in data and data['email'].strip():
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                if not User.validate_email(new_email):
                    return jsonify({'message': 'Email inválido'}), 400
                
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user:
                    return jsonify({'message': 'Email já está em uso'}), 409
                
                user.email = new_email
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'profile': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/picture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        if 'picture' not in request.files:
            return jsonify({'message': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['picture']
        
        if file.filename == '':
            return jsonify({'message': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar tamanho do arquivo
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'message': 'Arquivo muito grande. Máximo 5MB'}), 400
        
        # Remover foto anterior se existir
        if user.profile_picture:
            try:
                old_picture_path = os.path.join(current_app.static_folder, user.profile_picture)
                if os.path.exists(old_picture_path):
                    os.remove(old_picture_path)
            except Exception as e:
                current_app.logger.warning(f"Erro ao remover foto anterior: {str(e)}")
        
        # Salvar nova foto
        picture_path = save_profile_picture(file)
        
        if not picture_path:
            return jsonify({'message': 'Erro ao processar imagem'}), 400
        
        user.profile_picture = picture_path
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Foto de perfil atualizada com sucesso',
            'profile_picture': picture_path
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao fazer upload da foto: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            return jsonify({'message': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar senha atual
        if not user.check_password(current_password):
            return jsonify({'message': 'Senha atual incorreta'}), 400
        
        # Validar nova senha
        if len(new_password) < 6:
            return jsonify({'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        if new_password != confirm_password:
            return jsonify({'message': 'Confirmação de senha não confere'}), 400
        
        # Atualizar senha
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao alterar senha: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/complaints', methods=['GET'])
@jwt_required()
def get_user_complaints():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Parâmetros de filtro
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query base
        query = Complaint.query.filter_by(user_id=current_user_id)
        
        # Aplicar filtro de status se fornecido
        if status:
            query = query.filter_by(status=status)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(desc(Complaint.created_at))
        
        # Paginação
        complaints = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        complaints_data = [complaint.to_dict() for complaint in complaints.items]
        
        return jsonify({
            'complaints': complaints_data,
            'pagination': {
                'page': complaints.page,
                'pages': complaints.pages,
                'per_page': complaints.per_page,
                'total': complaints.total,
                'has_next': complaints.has_next,
                'has_prev': complaints.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar reclamações do usuário: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/notifications', methods=['GET'])
@jwt_required()
def get_user_notifications():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Parâmetros
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Query base
        query = Notification.query.filter_by(user_id=current_user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(desc(Notification.created_at))
        
        # Paginação
        notifications = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        notifications_data = [notification.to_dict() for notification in notifications.items]
        
        # Contar notificações não lidas
        unread_count = Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).count()
        
        return jsonify({
            'notifications': notifications_data,
            'unread_count': unread_count,
            'pagination': {
                'page': notifications.page,
                'pages': notifications.pages,
                'per_page': notifications.per_page,
                'total': notifications.total,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar notificações: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    try:
        current_user_id = get_jwt_identity()
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user_id
        ).first()
        
        if not notification:
            return jsonify({'message': 'Notificação não encontrada'}), 404
        
        notification.mark_as_read()
        
        return jsonify({'message': 'Notificação marcada como lida'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao marcar notificação como lida: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    try:
        current_user_id = get_jwt_identity()
        
        Notification.query.filter_by(
            user_id=current_user_id,
            is_read=False
        ).update({'is_read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'Todas as notificações foram marcadas como lidas'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao marcar todas as notificações como lidas: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@profile_bp.route('/profile/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_account():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'message': 'Senha é obrigatória para desativar a conta'}), 400
        
        if not user.check_password(password):
            return jsonify({'message': 'Senha incorreta'}), 400
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Conta desativada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao desativar conta: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

