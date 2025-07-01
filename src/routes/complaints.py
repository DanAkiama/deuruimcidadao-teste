from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db
from src.models.user import User
from src.models.complaint import Complaint, Vote, Response
from src.models.notification import Notification
from sqlalchemy import or_, and_, func, desc
from datetime import datetime, timedelta
import os
import uuid
from werkzeug.utils import secure_filename

complaints_bp = Blueprint('complaints', __name__)

# Configurações para upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """Salva arquivo enviado e retorna o caminho"""
    if file and allowed_file(file.filename):
        # Criar diretório se não existir
        upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_path, unique_filename)
        
        file.save(file_path)
        return f"{UPLOAD_FOLDER}/{unique_filename}"
    return None

@complaints_bp.route('/complaints', methods=['POST'])
@jwt_required()
def create_complaint():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Obter dados do formulário
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        subcategory = request.form.get('subcategory', '').strip()
        address = request.form.get('address', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        tags = request.form.get('tags', '').strip()
        
        # Validações
        if not title or len(title) < 5:
            return jsonify({'message': 'Título deve ter pelo menos 5 caracteres'}), 400
        
        if not description or len(description) < 10:
            return jsonify({'message': 'Descrição deve ter pelo menos 10 caracteres'}), 400
        
        if not category:
            return jsonify({'message': 'Categoria é obrigatória'}), 400
        
        # Processar coordenadas
        lat = float(latitude) if latitude else None
        lng = float(longitude) if longitude else None
        
        # Processar upload de arquivo
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            image_path = save_uploaded_file(file)
        
        # Determinar prioridade baseada na categoria
        priority_map = {
            'buraco': 'alta',
            'iluminacao': 'alta',
            'seguranca': 'urgente',
            'saude': 'alta',
            'transporte': 'normal',
            'lixo': 'normal',
            'outros': 'normal'
        }
        priority = priority_map.get(category, 'normal')
        
        # Criar reclamação
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            subcategory=subcategory,
            address=address,
            latitude=lat,
            longitude=lng,
            city=user.city,
            image_path=image_path,
            priority=priority,
            user_id=current_user_id,
            tags=tags
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        # Criar notificação para o usuário
        Notification.create_notification(
            user_id=current_user_id,
            complaint_id=complaint.id,
            type='complaint_created',
            title='Reclamação Registrada',
            message=f'Sua reclamação "{title}" foi registrada com sucesso e está sendo analisada.'
        )
        
        # Adicionar pontos de gamificação
        user.add_points(10, 'complaint_created')
        
        return jsonify({
            'message': 'Reclamação criada com sucesso',
            'complaint': complaint.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao criar reclamação: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints', methods=['GET'])
def get_complaints():
    try:
        # Parâmetros de filtro
        city = request.args.get('city', 'cuiaba')
        category = request.args.get('category')
        status = request.args.get('status')
        priority = request.args.get('priority')
        search = request.args.get('search')
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        radius = request.args.get('radius', 5)  # km
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        order = request.args.get('order', 'desc')
        
        # Query base
        query = Complaint.query.filter_by(city=city.lower())
        
        # Aplicar filtros
        if category:
            query = query.filter_by(category=category)
        
        if status:
            query = query.filter_by(status=status)
        
        if priority:
            query = query.filter_by(priority=priority)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Complaint.title.ilike(search_term),
                    Complaint.description.ilike(search_term),
                    Complaint.address.ilike(search_term),
                    Complaint.tags.ilike(search_term)
                )
            )
        
        # Filtro por proximidade geográfica
        if latitude and longitude:
            lat = float(latitude)
            lng = float(longitude)
            radius_km = float(radius)
            
            # Fórmula de Haversine simplificada para filtrar por proximidade
            query = query.filter(
                and_(
                    Complaint.latitude.isnot(None),
                    Complaint.longitude.isnot(None),
                    func.abs(Complaint.latitude - lat) < (radius_km / 111.0),  # Aproximação
                    func.abs(Complaint.longitude - lng) < (radius_km / 111.0)
                )
            )
        
        # Ordenação
        if sort_by == 'votes':
            # Ordenar por número de votos
            query = query.outerjoin(Vote).group_by(Complaint.id).order_by(
                desc(func.count(Vote.id)) if order == 'desc' else func.count(Vote.id)
            )
        elif sort_by == 'priority':
            # Ordenação customizada por prioridade
            priority_order = {'urgente': 4, 'alta': 3, 'normal': 2, 'baixa': 1}
            if order == 'desc':
                query = query.order_by(
                    func.case(
                        (Complaint.priority == 'urgente', 4),
                        (Complaint.priority == 'alta', 3),
                        (Complaint.priority == 'normal', 2),
                        (Complaint.priority == 'baixa', 1),
                        else_=0
                    ).desc()
                )
            else:
                query = query.order_by(
                    func.case(
                        (Complaint.priority == 'urgente', 4),
                        (Complaint.priority == 'alta', 3),
                        (Complaint.priority == 'normal', 2),
                        (Complaint.priority == 'baixa', 1),
                        else_=0
                    )
                )
        else:
            # Ordenação padrão por campo
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
        
        # Converter para dict e incluir informações extras
        complaints_data = []
        for complaint in complaints.items:
            complaint_dict = complaint.to_dict()
            complaint_dict['user'] = {
                'id': complaint.user.id,
                'username': complaint.user.username,
                'full_name': complaint.user.full_name
            }
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
        current_app.logger.error(f"Erro ao buscar reclamações: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    try:
        complaint = Complaint.query.get_or_404(complaint_id)
        
        complaint_dict = complaint.to_dict()
        complaint_dict['user'] = {
            'id': complaint.user.id,
            'username': complaint.user.username,
            'full_name': complaint.user.full_name
        }
        
        # Incluir respostas da administração
        responses = [response.to_dict() for response in complaint.responses]
        complaint_dict['responses'] = responses
        
        return jsonify({'complaint': complaint_dict}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar reclamação: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/<int:complaint_id>/vote', methods=['POST'])
@jwt_required()
def vote_complaint(complaint_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        complaint = Complaint.query.get_or_404(complaint_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se já votou
        existing_vote = Vote.query.filter_by(
            user_id=current_user_id,
            complaint_id=complaint_id
        ).first()
        
        if existing_vote:
            # Remover voto (toggle)
            db.session.delete(existing_vote)
            message = 'Voto removido'
            user.add_points(-2, 'vote_removed')
        else:
            # Adicionar voto
            vote = Vote(user_id=current_user_id, complaint_id=complaint_id)
            db.session.add(vote)
            message = 'Voto adicionado'
            user.add_points(2, 'vote_added')
        
        db.session.commit()
        
        return jsonify({
            'message': message,
            'vote_count': complaint.get_vote_count()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao votar: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/<int:complaint_id>', methods=['PUT'])
@jwt_required()
def update_complaint(complaint_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        complaint = Complaint.query.get_or_404(complaint_id)
        
        # Verificar permissões
        if complaint.user_id != current_user_id and user.role != 'responsavel':
            return jsonify({'message': 'Sem permissão para editar esta reclamação'}), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'title' in data and data['title'].strip():
            complaint.title = data['title'].strip()
        
        if 'description' in data and data['description'].strip():
            complaint.description = data['description'].strip()
        
        if 'category' in data and data['category'].strip():
            complaint.category = data['category'].strip()
        
        if 'subcategory' in data:
            complaint.subcategory = data['subcategory'].strip()
        
        if 'address' in data:
            complaint.address = data['address'].strip()
        
        if 'tags' in data:
            complaint.tags = data['tags'].strip()
        
        # Apenas responsáveis podem alterar status e prioridade
        if user.role == 'responsavel':
            if 'status' in data:
                old_status = complaint.status
                complaint.status = data['status']
                
                # Criar notificação se status mudou
                if old_status != complaint.status:
                    status_messages = {
                        'respondida': 'Sua reclamação foi respondida pela administração.',
                        'resolvido': 'Sua reclamação foi marcada como resolvida!'
                    }
                    
                    if complaint.status in status_messages:
                        Notification.create_notification(
                            user_id=complaint.user_id,
                            complaint_id=complaint.id,
                            type='status_updated',
                            title='Status Atualizado',
                            message=status_messages[complaint.status]
                        )
                    
                    if complaint.status == 'resolvido':
                        complaint.resolved_at = datetime.utcnow()
                        # Dar pontos extras para o usuário que fez a reclamação
                        complaint.user.add_points(20, 'complaint_resolved')
            
            if 'priority' in data:
                complaint.priority = data['priority']
            
            if 'admin_response' in data:
                complaint.admin_response = data['admin_response']
                complaint.admin_user_id = current_user_id
        
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Reclamação atualizada com sucesso',
            'complaint': complaint.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao atualizar reclamação: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/<int:complaint_id>', methods=['DELETE'])
@jwt_required()
def delete_complaint(complaint_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        complaint = Complaint.query.get_or_404(complaint_id)
        
        # Verificar permissões
        if complaint.user_id != current_user_id and user.role != 'responsavel':
            return jsonify({'message': 'Sem permissão para deletar esta reclamação'}), 403
        
        # Remover arquivo de imagem se existir
        if complaint.image_path:
            try:
                image_full_path = os.path.join(current_app.static_folder, complaint.image_path)
                if os.path.exists(image_full_path):
                    os.remove(image_full_path)
            except Exception as e:
                current_app.logger.warning(f"Erro ao remover imagem: {str(e)}")
        
        db.session.delete(complaint)
        db.session.commit()
        
        return jsonify({'message': 'Reclamação deletada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao deletar reclamação: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/similar', methods=['POST'])
def find_similar_complaints():
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        city = data.get('city', 'cuiaba').lower()
        
        if not title and not description:
            return jsonify({'similar_complaints': []}), 200
        
        # Buscar reclamações similares
        search_terms = []
        if title:
            search_terms.extend(title.split())
        if description:
            search_terms.extend(description.split()[:10])  # Primeiras 10 palavras
        
        if not search_terms:
            return jsonify({'similar_complaints': []}), 200
        
        # Criar query para busca de similaridade
        conditions = []
        for term in search_terms:
            if len(term) > 3:  # Ignorar palavras muito pequenas
                term_pattern = f"%{term}%"
                conditions.append(
                    or_(
                        Complaint.title.ilike(term_pattern),
                        Complaint.description.ilike(term_pattern)
                    )
                )
        
        if not conditions:
            return jsonify({'similar_complaints': []}), 200
        
        similar_complaints = Complaint.query.filter(
            and_(
                Complaint.city == city,
                or_(*conditions)
            )
        ).limit(5).all()
        
        complaints_data = []
        for complaint in similar_complaints:
            complaint_dict = complaint.to_dict()
            complaint_dict['similarity_score'] = len([
                term for term in search_terms 
                if term.lower() in complaint.title.lower() or term.lower() in complaint.description.lower()
            ])
            complaints_data.append(complaint_dict)
        
        # Ordenar por score de similaridade
        complaints_data.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return jsonify({'similar_complaints': complaints_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar reclamações similares: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@complaints_bp.route('/complaints/categories', methods=['GET'])
def get_categories():
    """Retorna categorias e subcategorias disponíveis"""
    categories = {
        'buraco': {
            'name': 'Buracos e Pavimentação',
            'subcategories': ['Buraco na rua', 'Asfalto danificado', 'Calçada quebrada', 'Meio-fio danificado']
        },
        'iluminacao': {
            'name': 'Iluminação Pública',
            'subcategories': ['Poste queimado', 'Falta de iluminação', 'Poste caído', 'Fiação exposta']
        },
        'lixo': {
            'name': 'Limpeza e Lixo',
            'subcategories': ['Lixo acumulado', 'Entulho abandonado', 'Falta de coleta', 'Container danificado']
        },
        'transporte': {
            'name': 'Transporte Público',
            'subcategories': ['Ponto de ônibus danificado', 'Falta de sinalização', 'Atraso frequente', 'Veículo em mau estado']
        },
        'saude': {
            'name': 'Saúde Pública',
            'subcategories': ['Foco de dengue', 'Esgoto a céu aberto', 'Água parada', 'Falta de saneamento']
        },
        'educacao': {
            'name': 'Educação',
            'subcategories': ['Escola em mau estado', 'Falta de professor', 'Equipamentos danificados', 'Segurança escolar']
        },
        'seguranca': {
            'name': 'Segurança',
            'subcategories': ['Falta de policiamento', 'Semáforo quebrado', 'Placa de trânsito danificada', 'Local perigoso']
        },
        'outros': {
            'name': 'Outros',
            'subcategories': ['Barulho excessivo', 'Poluição', 'Problema ambiental', 'Outros problemas']
        }
    }
    
    return jsonify({'categories': categories}), 200

