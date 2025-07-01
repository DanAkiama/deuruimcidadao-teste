"""
Casos de Uso de Notificações

Contém a lógica de aplicação para operações relacionadas a notificações,
incluindo envio, marcação como lida e listagem.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..domain.entities.notification import Notification, NotificationType, NotificationChannel
from ..infrastructure.db.database import db
from ..infrastructure.db.models import NotificationModel, UserModel


class SendNotificationUseCase:
    """Caso de uso para envio de notificações."""
    
    def execute(self, notification_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa o envio de uma notificação.
        
        Args:
            notification_data: Dados da notificação
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_notificacao)
        """
        try:
            # Verificar se o usuário existe
            user_model = UserModel.query.get(notification_data['user_id'])
            if not user_model:
                return False, "Usuário não encontrado", None
            
            # Criar entidade de domínio para validação
            notification_entity = Notification(
                id=None,
                user_id=notification_data['user_id'],
                title=notification_data['title'],
                message=notification_data['message'],
                notification_type=notification_data['notification_type'],
                channel=notification_data['channel'],
                related_complaint_id=notification_data.get('related_complaint_id'),
                metadata=notification_data.get('metadata'),
                created_at=datetime.utcnow()
            )
            
            # Criar modelo para persistência
            notification_model = NotificationModel(
                user_id=notification_entity.user_id,
                title=notification_entity.title,
                message=notification_entity.message,
                notification_type=notification_entity.notification_type,
                channel=notification_entity.channel,
                related_complaint_id=notification_entity.related_complaint_id,
                extra_data=notification_entity.metadata
            )
            
            # Salvar no banco
            db.session.add(notification_model)
            db.session.commit()
            
            # Atualizar entidade com dados persistidos
            notification_entity.id = notification_model.id
            notification_entity.created_at = notification_model.created_at
            
            # Marcar como enviada (simulação)
            notification_entity.mark_as_sent()
            notification_model.is_sent = True
            notification_model.sent_at = notification_entity.sent_at
            db.session.commit()
            
            return True, "Notificação enviada com sucesso", notification_entity.to_dict()
            
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None


class MarkNotificationAsReadUseCase:
    """Caso de uso para marcar notificação como lida."""
    
    def execute(self, user_id: int, notification_id: int) -> Tuple[bool, str]:
        """
        Executa a marcação de uma notificação como lida.
        
        Args:
            user_id: ID do usuário
            notification_id: ID da notificação
            
        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        try:
            # Buscar notificação
            notification_model = NotificationModel.query.filter_by(
                id=notification_id,
                user_id=user_id
            ).first()
            
            if not notification_model:
                return False, "Notificação não encontrada"
            
            # Marcar como lida
            if not notification_model.is_read:
                notification_model.is_read = True
                notification_model.read_at = datetime.utcnow()
                db.session.commit()
            
            return True, "Notificação marcada como lida"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}"


class GetUserNotificationsUseCase:
    """Caso de uso para obter notificações do usuário."""
    
    def execute(self, user_id: int, filters: Dict = None) -> Tuple[bool, str, Optional[List[Dict]]]:
        """
        Executa a busca de notificações do usuário.
        
        Args:
            user_id: ID do usuário
            filters: Filtros para a busca
            
        Returns:
            Tupla contendo (sucesso, mensagem, lista_notificacoes)
        """
        try:
            query = NotificationModel.query.filter_by(user_id=user_id)
            
            # Aplicar filtros
            if filters:
                if 'is_read' in filters:
                    query = query.filter(NotificationModel.is_read == filters['is_read'])
                
                if 'notification_type' in filters:
                    query = query.filter(NotificationModel.notification_type == filters['notification_type'])
                
                if 'channel' in filters:
                    query = query.filter(NotificationModel.channel == filters['channel'])
            
            # Ordenar por data de criação (mais recentes primeiro)
            notifications = query.order_by(NotificationModel.created_at.desc()).all()
            
            # Converter para dicionários
            notifications_data = [self._model_to_dict(n) for n in notifications]
            
            return True, "Notificações encontradas", notifications_data
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}", None
    
    def _model_to_dict(self, notification_model: NotificationModel) -> Dict:
        """Converte modelo para dicionário."""
        return {
            'id': notification_model.id,
            'user_id': notification_model.user_id,
            'title': notification_model.title,
            'message': notification_model.message,
            'notification_type': notification_model.notification_type,
            'channel': notification_model.channel,
            'is_read': notification_model.is_read,
            'is_sent': notification_model.is_sent,
            'related_complaint_id': notification_model.related_complaint_id,
            'metadata': notification_model.extra_data,
            'created_at': notification_model.created_at.isoformat() if notification_model.created_at else None,
            'read_at': notification_model.read_at.isoformat() if notification_model.read_at else None,
            'sent_at': notification_model.sent_at.isoformat() if notification_model.sent_at else None
        }


class GetUnreadNotificationsCountUseCase:
    """Caso de uso para obter contagem de notificações não lidas."""
    
    def execute(self, user_id: int) -> Tuple[bool, str, Optional[int]]:
        """
        Executa a contagem de notificações não lidas.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Tupla contendo (sucesso, mensagem, contagem)
        """
        try:
            count = NotificationModel.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            
            return True, "Contagem obtida", count
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}", None


class CreateComplaintNotificationUseCase:
    """Caso de uso para criar notificações relacionadas a reclamações."""
    
    def execute(self, complaint_id: int, notification_type: str, target_users: List[int] = None) -> Tuple[bool, str]:
        """
        Cria notificações para eventos relacionados a reclamações.
        
        Args:
            complaint_id: ID da reclamação
            notification_type: Tipo da notificação
            target_users: Lista de IDs de usuários (opcional)
            
        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        try:
            from ..infrastructure.db.models import ComplaintModel
            
            # Buscar reclamação
            complaint_model = ComplaintModel.query.get(complaint_id)
            if not complaint_model:
                return False, "Reclamação não encontrada"
            
            # Definir usuários alvo
            if target_users is None:
                target_users = [complaint_model.user_id]
            
            # Definir título e mensagem baseado no tipo
            title, message = self._get_notification_content(notification_type, complaint_model)
            
            # Criar notificações para cada usuário
            for user_id in target_users:
                notification_data = {
                    'user_id': user_id,
                    'title': title,
                    'message': message,
                    'notification_type': notification_type,
                    'channel': NotificationChannel.IN_APP.value,
                    'related_complaint_id': complaint_id
                }
                
                send_usecase = SendNotificationUseCase()
                send_usecase.execute(notification_data)
            
            return True, "Notificações criadas com sucesso"
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}"
    
    def _get_notification_content(self, notification_type: str, complaint_model) -> Tuple[str, str]:
        """Gera título e mensagem baseado no tipo de notificação."""
        if notification_type == NotificationType.COMPLAINT_RESPONDED.value:
            title = "Reclamação Respondida"
            message = f"Sua reclamação '{complaint_model.title}' foi respondida por um gestor."
        
        elif notification_type == NotificationType.COMPLAINT_RESOLVED.value:
            title = "Reclamação Resolvida"
            message = f"Sua reclamação '{complaint_model.title}' foi marcada como resolvida."
        
        elif notification_type == NotificationType.COMPLAINT_VOTED.value:
            title = "Nova Votação"
            message = f"Sua reclamação '{complaint_model.title}' recebeu um novo voto."
        
        else:
            title = "Atualização da Reclamação"
            message = f"Há uma atualização na sua reclamação '{complaint_model.title}'."
        
        return title, message

