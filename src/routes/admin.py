from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.complaint import Complaint, Vote, Response
from src.models.notification import Notification
from src.models.gamification import CityRanking, UserPoints, Badge
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
import calendar

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """Decorator para verificar se o usuário é administrador"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role != 'responsavel':
                return jsonify({'message': 'Acesso negado. Apenas administradores.'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@admin_bp.route('/admin/dashboard', methods=['GET'])
@jwt_required()
@require_admin()
def get_dashboard():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        city = user.city
        
        # Estatísticas gerais
        total_complaints = Complaint.query.filter_by(city=city).count()
        pending_complaints = Complaint.query.filter_by(city=city, status='pendente').count()
        in_progress_complaints = Complaint.query.filter_by(city=city, status='respondida').count()
        resolved_complaints = Complaint.query.filter_by(city=city, status='resolvido').count()
        
        # Estatísticas por categoria
        category_stats = db.session.query(
            Complaint.category,
            func.count(Complaint.id).label('count')
        ).filter_by(city=city).group_by(Complaint.category).all()
        
        # Estatísticas por prioridade
        priority_stats = db.session.query(
            Complaint.priority,
            func.count(Complaint.id).label('count')
        ).filter_by(city=city).group_by(Complaint.priority).all()
        
        # Reclamações mais votadas (top 10)
        top_voted = db.session.query(
            Complaint,
            func.count(Vote.id).label('vote_count')
        ).outerjoin(Vote).filter(
            Complaint.city == city
        ).group_by(Complaint.id).order_by(
            desc('vote_count')
        ).limit(10).all()
        
        # Estatísticas mensais (últimos 6 meses)
        monthly_stats = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            
            month_complaints = Complaint.query.filter(
                and_(
                    Complaint.city == city,
                    Complaint.created_at >= month_start,
                    Complaint.created_at <= month_end
                )
            ).count()
            
            month_resolved = Complaint.query.filter(
                and_(
                    Complaint.city == city,
                    Complaint.resolved_at >= month_start,
                    Complaint.resolved_at <= month_end
                )
            ).count()
            
            monthly_stats.append({
                'month': calendar.month_name[date.month],
                'year': date.year,
                'complaints': month_complaints,
                'resolved': month_resolved
            })
        
        # Usuários mais ativos
        active_users = db.session.query(
            User,
            func.count(Complaint.id).label('complaint_count')
        ).outerjoin(Complaint).filter(
            User.city == city
        ).group_by(User.id).order_by(
            desc('complaint_count')
        ).limit(10).all()
        
        # Tempo médio de resolução
        resolved_with_time = Complaint.query.filter(
            and_(
                Complaint.city == city,
                Complaint.status == 'resolvido',
                Complaint.resolved_at.isnot(None)
            )
        ).all()
        
        avg_resolution_time = 0
        if resolved_with_time:
            total_time = sum([
                (complaint.resolved_at - complaint.created_at).days 
                for complaint in resolved_with_time
            ])
            avg_resolution_time = total_time / len(resolved_with_time)
        
        dashboard_data = {
            'overview': {
                'total_complaints': total_complaints,
                'pending_complaints': pending_complaints,
                'in_progress_complaints': in_progress_complaints,
                'resolved_complaints': resolved_complaints,
                'resolution_rate': (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0,
                'avg_resolution_time_days': round(avg_resolution_time, 1)
            },
            'category_stats': [{'category': cat, 'count': count} for cat, count in category_stats],
            'priority_stats': [{'priority': pri, 'count': count} for pri, count in priority_stats],
            'top_voted_complaints': [
                {
                    'complaint': complaint.to_dict(),
                    'vote_count': vote_count
                } for complaint, vote_count in top_voted
            ],
            'monthly_stats': list(reversed(monthly_stats)),
            'active_users': [
                {
                    'user': user.to_dict(),
                    'complaint_count': count
                } for user, count in active_users
            ]
        }
        
        return jsonify({'dashboard': dashboard_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar dashboard: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/complaints', methods=['GET'])
@jwt_required()
@require_admin()
def get_admin_complaints():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        city = user.city
        
        # Parâmetros de filtro
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        search = request.args.get('search')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        # Query base
        query = Complaint.query.filter_by(city=city)
        
        # Aplicar filtros
        if status:
            query = query.filter_by(status=status)
        
        if category:
            query = query.filter_by(category=category)
        
        if priority:
            query = query.filter_by(priority=priority)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Complaint.title.ilike(search_term),
                    Complaint.description.ilike(search_term),
                    Complaint.address.ilike(search_term)
                )
            )
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Complaint.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Complaint.created_at < date_to_obj)
            except ValueError:
                pass
        
        # Ordenação
        if sort_by == 'votes':
            query = query.outerjoin(Vote).group_by(Complaint.id).order_by(
                desc(func.count(Vote.id)) if order == 'desc' else func.count(Vote.id)
            )
        else:
            field = getattr(Complaint, sort_by, Complaint.created_at)
            if order == 'desc':
                query = query.order_by(desc(field))
            else:
                query = query.order_by(field)
        
        # Paginação
        complaints = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Converter para dict com informações extras
        complaints_data = []
        for complaint in complaints.items:
            complaint_dict = complaint.to_dict()
            complaint_dict['user'] = {
                'id': complaint.user.id,
                'username': complaint.user.username,
                'full_name': complaint.user.full_name,
                'email': complaint.user.email,
                'phone': complaint.user.phone
            }
            complaint_dict['days_since_created'] = (datetime.utcnow() - complaint.created_at).days
            complaints_data.append(complaint_dict)
        
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
        current_app.logger.error(f"Erro ao buscar reclamações admin: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/complaints/<int:complaint_id>/respond', methods=['POST'])
@jwt_required()
@require_admin()
def respond_to_complaint(complaint_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        complaint = Complaint.query.get_or_404(complaint_id)
        
        # Verificar se a reclamação é da mesma cidade
        if complaint.city != user.city:
            return jsonify({'message': 'Sem permissão para responder esta reclamação'}), 403
        
        data = request.get_json()
        message = data.get('message', '').strip()
        new_status = data.get('status')
        
        if not message:
            return jsonify({'message': 'Mensagem é obrigatória'}), 400
        
        # Criar resposta
        response = Response(
            complaint_id=complaint_id,
            admin_user_id=current_user_id,
            message=message
        )
        db.session.add(response)
        
        # Atualizar status se fornecido
        if new_status and new_status in ['pendente', 'respondida', 'resolvido']:
            old_status = complaint.status
            complaint.status = new_status
            complaint.admin_response = message
            complaint.admin_user_id = current_user_id
            
            if new_status == 'resolvido' and old_status != 'resolvido':
                complaint.resolved_at = datetime.utcnow()
                # Dar pontos extras para o usuário
                complaint.user.add_points(20, 'complaint_resolved')
        
        complaint.updated_at = datetime.utcnow()
        
        # Criar notificação para o usuário
        status_messages = {
            'respondida': 'Sua reclamação foi respondida pela administração.',
            'resolvido': 'Sua reclamação foi marcada como resolvida!'
        }
        
        notification_message = status_messages.get(new_status, 'Nova resposta em sua reclamação.')
        
        Notification.create_notification(
            user_id=complaint.user_id,
            complaint_id=complaint_id,
            type='response_added',
            title='Nova Resposta',
            message=f'{notification_message}\n\nResposta: {message}'
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Resposta enviada com sucesso',
            'response': response.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao responder reclamação: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/complaints/<int:complaint_id>/priority', methods=['PUT'])
@jwt_required()
@require_admin()
def update_complaint_priority(complaint_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        complaint = Complaint.query.get_or_404(complaint_id)
        
        if complaint.city != user.city:
            return jsonify({'message': 'Sem permissão para alterar esta reclamação'}), 403
        
        data = request.get_json()
        new_priority = data.get('priority')
        
        if new_priority not in ['baixa', 'normal', 'alta', 'urgente']:
            return jsonify({'message': 'Prioridade inválida'}), 400
        
        old_priority = complaint.priority
        complaint.priority = new_priority
        complaint.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Notificar usuário se prioridade aumentou
        if new_priority in ['alta', 'urgente'] and old_priority in ['baixa', 'normal']:
            Notification.create_notification(
                user_id=complaint.user_id,
                complaint_id=complaint_id,
                type='priority_updated',
                title='Prioridade Atualizada',
                message=f'Sua reclamação foi marcada como prioridade {new_priority}.'
            )
        
        return jsonify({
            'message': 'Prioridade atualizada com sucesso',
            'complaint': complaint.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar prioridade: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@require_admin()
def get_admin_users():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        city = user.city
        
        # Parâmetros
        search = request.args.get('search')
        role = request.args.get('role')
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Query base
        query = User.query.filter_by(city=city)
        
        # Aplicar filtros
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        if role:
            query = query.filter_by(role=role)
        
        if is_active is not None:
            active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=active_bool)
        
        # Ordenar por data de criação
        query = query.order_by(desc(User.created_at))
        
        # Paginação
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Converter para dict com estatísticas
        users_data = []
        for user_item in users.items:
            user_dict = user_item.to_dict()
            
            # Adicionar estatísticas
            complaints_count = Complaint.query.filter_by(user_id=user_item.id).count()
            resolved_count = Complaint.query.filter_by(
                user_id=user_item.id, 
                status='resolvido'
            ).count()
            
            user_dict['statistics'] = {
                'complaints_count': complaints_count,
                'resolved_count': resolved_count
            }
            
            users_data.append(user_dict)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar usuários: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/reports/export', methods=['GET'])
@jwt_required()
@require_admin()
def export_reports():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        city = user.city
        
        # Parâmetros
        report_type = request.args.get('type', 'complaints')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if report_type == 'complaints':
            query = Complaint.query.filter_by(city=city)
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                    query = query.filter(Complaint.created_at >= date_from_obj)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Complaint.created_at < date_to_obj)
                except ValueError:
                    pass
            
            complaints = query.order_by(desc(Complaint.created_at)).all()
            
            report_data = []
            for complaint in complaints:
                report_data.append({
                    'id': complaint.id,
                    'titulo': complaint.title,
                    'categoria': complaint.category,
                    'status': complaint.status,
                    'prioridade': complaint.priority,
                    'endereco': complaint.address,
                    'usuario': complaint.user.full_name,
                    'email_usuario': complaint.user.email,
                    'data_criacao': complaint.created_at.strftime('%d/%m/%Y %H:%M'),
                    'data_resolucao': complaint.resolved_at.strftime('%d/%m/%Y %H:%M') if complaint.resolved_at else '',
                    'votos': complaint.get_vote_count()
                })
            
            return jsonify({
                'report_type': 'complaints',
                'city': city,
                'date_range': f"{date_from or 'início'} até {date_to or 'hoje'}",
                'total_records': len(report_data),
                'data': report_data
            }), 200
        
        return jsonify({'message': 'Tipo de relatório não suportado'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar relatório: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/admin/ranking/update', methods=['POST'])
@jwt_required()
@require_admin()
def update_city_ranking():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        city = user.city
        
        # Atualizar ranking da cidade
        CityRanking.update_monthly_ranking(city)
        
        return jsonify({'message': 'Ranking atualizado com sucesso'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao atualizar ranking: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

