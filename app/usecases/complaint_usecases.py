"""
Casos de Uso de Reclamações

Contém a lógica de aplicação para operações relacionadas a reclamações,
incluindo criação, atualização, votação e gerenciamento.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..domain.entities.complaint import Complaint, ComplaintStatus
from ..domain.entities.user import User
from ..infrastructure.db.database import db
from ..infrastructure.db.models import ComplaintModel, UserModel, VoteModel


class CreateComplaintUseCase:
    """Caso de uso para criação de reclamações."""
    
    def execute(self, user_id: int, complaint_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa a criação de uma nova reclamação.
        
        Args:
            user_id: ID do usuário que está criando a reclamação
            complaint_data: Dados da reclamação
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_reclamacao)
        """
        try:
            # Verificar se o usuário existe e pode criar reclamações
            user_model = UserModel.query.get(user_id)
            if not user_model or not user_model.is_active:
                return False, "Usuário não encontrado ou inativo", None
            
            # Criar entidade de domínio para validação
            complaint_entity = Complaint(
                id=None,
                title=complaint_data['title'],
                description=complaint_data['description'],
                category=complaint_data['category'],
                user_id=user_id,
                city=user_model.city,
                subcategory=complaint_data.get('subcategory'),
                address=complaint_data.get('address'),
                latitude=complaint_data.get('latitude'),
                longitude=complaint_data.get('longitude'),
                image_path=complaint_data.get('image_path'),
                priority=complaint_data.get('priority', 'normal'),
                tags=complaint_data.get('tags'),
                created_at=datetime.utcnow()
            )
            
            # Criar modelo para persistência
            complaint_model = ComplaintModel(
                title=complaint_entity.title,
                description=complaint_entity.description,
                category=complaint_entity.category,
                subcategory=complaint_entity.subcategory,
                address=complaint_entity.address,
                latitude=complaint_entity.latitude,
                longitude=complaint_entity.longitude,
                city=complaint_entity.city,
                image_path=complaint_entity.image_path,
                priority=complaint_entity.priority,
                tags=complaint_entity.tags,
                user_id=user_id
            )
            
            # Salvar no banco
            db.session.add(complaint_model)
            db.session.commit()
            
            # Atualizar entidade com dados persistidos
            complaint_entity.id = complaint_model.id
            complaint_entity.created_at = complaint_model.created_at
            
            return True, "Reclamação criada com sucesso", complaint_entity.to_dict()
            
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None


class UpdateComplaintUseCase:
    """Caso de uso para atualização de reclamações."""
    
    def execute(self, user_id: int, complaint_id: int, update_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa a atualização de uma reclamação.
        
        Args:
            user_id: ID do usuário que está atualizando
            complaint_id: ID da reclamação
            update_data: Dados para atualização
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_reclamacao)
        """
        try:
            # Buscar reclamação
            complaint_model = ComplaintModel.query.get(complaint_id)
            if not complaint_model:
                return False, "Reclamação não encontrada", None
            
            # Verificar permissões
            if complaint_model.user_id != user_id:
                return False, "Você não tem permissão para editar esta reclamação", None
            
            # Converter para entidade
            complaint_entity = self._model_to_entity(complaint_model)
            
            # Verificar se pode ser editada
            if not complaint_entity.can_be_edited_by_user(user_id):
                return False, "Esta reclamação não pode mais ser editada", None
            
            # Atualizar campos permitidos
            allowed_fields = ['title', 'description', 'category', 'subcategory', 'address', 'priority', 'tags']
            for field in allowed_fields:
                if field in update_data:
                    setattr(complaint_model, field, update_data[field])
            
            complaint_model.updated_at = datetime.utcnow()
            
            # Validar através da entidade
            updated_entity = self._model_to_entity(complaint_model)
            
            # Salvar no banco
            db.session.commit()
            
            return True, "Reclamação atualizada com sucesso", updated_entity.to_dict()
            
        except ValueError as e:
            db.session.rollback()
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None
    
    def _model_to_entity(self, complaint_model: ComplaintModel) -> Complaint:
        """Converte modelo para entidade."""
        return Complaint(
            id=complaint_model.id,
            title=complaint_model.title,
            description=complaint_model.description,
            category=complaint_model.category,
            user_id=complaint_model.user_id,
            city=complaint_model.city,
            subcategory=complaint_model.subcategory,
            address=complaint_model.address,
            latitude=complaint_model.latitude,
            longitude=complaint_model.longitude,
            image_path=complaint_model.image_path,
            status=complaint_model.status,
            priority=complaint_model.priority,
            tags=complaint_model.tags,
            admin_response=complaint_model.admin_response,
            admin_user_id=complaint_model.admin_user_id,
            created_at=complaint_model.created_at,
            updated_at=complaint_model.updated_at,
            resolved_at=complaint_model.resolved_at,
            vote_count=complaint_model.votes.count()
        )


class VoteComplaintUseCase:
    """Caso de uso para votação em reclamações."""
    
    def execute(self, user_id: int, complaint_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa a votação em uma reclamação.
        
        Args:
            user_id: ID do usuário que está votando
            complaint_id: ID da reclamação
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_voto)
        """
        try:
            # Verificar se o usuário existe
            user_model = UserModel.query.get(user_id)
            if not user_model or not user_model.is_active:
                return False, "Usuário não encontrado ou inativo", None
            
            # Verificar se a reclamação existe
            complaint_model = ComplaintModel.query.get(complaint_id)
            if not complaint_model:
                return False, "Reclamação não encontrada", None
            
            # Verificar se o usuário já votou
            existing_vote = VoteModel.query.filter_by(
                user_id=user_id, 
                complaint_id=complaint_id
            ).first()
            
            if existing_vote:
                # Remover voto (toggle)
                db.session.delete(existing_vote)
                db.session.commit()
                
                vote_count = VoteModel.query.filter_by(complaint_id=complaint_id).count()
                
                return True, "Voto removido com sucesso", {
                    'voted': False,
                    'vote_count': vote_count
                }
            else:
                # Adicionar voto
                vote_model = VoteModel(
                    user_id=user_id,
                    complaint_id=complaint_id
                )
                
                db.session.add(vote_model)
                db.session.commit()
                
                vote_count = VoteModel.query.filter_by(complaint_id=complaint_id).count()
                
                return True, "Voto adicionado com sucesso", {
                    'voted': True,
                    'vote_count': vote_count
                }
                
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None


class GetComplaintsUseCase:
    """Caso de uso para listagem de reclamações."""
    
    def execute(self, filters: Dict = None, user_id: int = None) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        Executa a busca de reclamações com filtros.
        
        Args:
            filters: Filtros para a busca
            user_id: ID do usuário (para verificar votos)
            
        Returns:
            Tupla contendo (sucesso, mensagem, lista_reclamacoes)
        """
        try:
            query = ComplaintModel.query
            
            # Aplicar filtros
            if filters:
                if 'city' in filters:
                    query = query.filter(ComplaintModel.city == filters['city'])
                
                if 'category' in filters:
                    query = query.filter(ComplaintModel.category == filters['category'])
                
                if 'status' in filters:
                    query = query.filter(ComplaintModel.status == filters['status'])
                
                if 'user_id' in filters:
                    query = query.filter(ComplaintModel.user_id == filters['user_id'])
            
            # Ordenar por data de criação (mais recentes primeiro)
            complaints = query.order_by(ComplaintModel.created_at.desc()).all()
            
            # Converter para dicionários
            complaints_data = []
            for complaint_model in complaints:
                complaint_dict = self._model_to_dict(complaint_model)
                
                # Adicionar informação de voto do usuário
                if user_id:
                    user_vote = VoteModel.query.filter_by(
                        user_id=user_id,
                        complaint_id=complaint_model.id
                    ).first()
                    complaint_dict['user_voted'] = user_vote is not None
                else:
                    complaint_dict['user_voted'] = False
                
                complaints_data.append(complaint_dict)
            
            return True, "Reclamações encontradas", complaints_data
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}", None
    
    def _model_to_dict(self, complaint_model: ComplaintModel) -> Dict:
        """Converte modelo para dicionário."""
        return {
            'id': complaint_model.id,
            'title': complaint_model.title,
            'description': complaint_model.description,
            'category': complaint_model.category,
            'subcategory': complaint_model.subcategory,
            'address': complaint_model.address,
            'latitude': complaint_model.latitude,
            'longitude': complaint_model.longitude,
            'city': complaint_model.city,
            'image_path': complaint_model.image_path,
            'status': complaint_model.status,
            'priority': complaint_model.priority,
            'tags': complaint_model.tags,
            'admin_response': complaint_model.admin_response,
            'user_id': complaint_model.user_id,
            'admin_user_id': complaint_model.admin_user_id,
            'created_at': complaint_model.created_at.isoformat() if complaint_model.created_at else None,
            'updated_at': complaint_model.updated_at.isoformat() if complaint_model.updated_at else None,
            'resolved_at': complaint_model.resolved_at.isoformat() if complaint_model.resolved_at else None,
            'vote_count': complaint_model.votes.count(),
            'user': {
                'id': complaint_model.user.id,
                'username': complaint_model.user.username,
                'full_name': complaint_model.user.full_name
            } if complaint_model.user else None
        }


class DeleteComplaintUseCase:
    """Caso de uso para exclusão de reclamações."""
    
    def execute(self, user_id: int, complaint_id: int) -> Tuple[bool, str]:
        """
        Executa a exclusão de uma reclamação.
        
        Args:
            user_id: ID do usuário que está excluindo
            complaint_id: ID da reclamação
            
        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        try:
            # Buscar reclamação
            complaint_model = ComplaintModel.query.get(complaint_id)
            if not complaint_model:
                return False, "Reclamação não encontrada"
            
            # Verificar permissões
            if complaint_model.user_id != user_id:
                return False, "Você não tem permissão para excluir esta reclamação"
            
            # Converter para entidade para validação
            complaint_entity = Complaint(
                id=complaint_model.id,
                title=complaint_model.title,
                description=complaint_model.description,
                category=complaint_model.category,
                user_id=complaint_model.user_id,
                city=complaint_model.city,
                status=complaint_model.status
            )
            
            # Verificar se pode ser excluída
            if not complaint_entity.can_be_edited_by_user(user_id):
                return False, "Esta reclamação não pode mais ser excluída"
            
            # Excluir do banco (cascade irá remover votos e respostas)
            db.session.delete(complaint_model)
            db.session.commit()
            
            return True, "Reclamação excluída com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}"

