"""
Entidade Notification - Representa uma notificação no sistema

Esta entidade contém as regras de negócio puras relacionadas às notificações,
sem dependências de frameworks ou infraestrutura.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class NotificationType(Enum):
    """Tipos possíveis para uma notificação."""
    COMPLAINT_CREATED = "complaint_created"
    COMPLAINT_RESPONDED = "complaint_responded"
    COMPLAINT_RESOLVED = "complaint_resolved"
    COMPLAINT_VOTED = "complaint_voted"
    SYSTEM_ANNOUNCEMENT = "system_announcement"


class NotificationChannel(Enum):
    """Canais possíveis para envio de notificação."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"
    IN_APP = "in_app"


@dataclass
class Notification:
    """
    Entidade que representa uma notificação no sistema.
    
    Contém as regras de negócio puras relacionadas às notificações,
    incluindo validações e lógicas específicas do domínio.
    """
    
    id: Optional[int]
    user_id: int
    title: str
    message: str
    notification_type: str
    channel: str
    is_read: bool = False
    is_sent: bool = False
    related_complaint_id: Optional[int] = None
    metadata: Optional[str] = None
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    def __post_init__(self):
        """Validações executadas após a criação do objeto."""
        self._validate_title()
        self._validate_message()
        self._validate_notification_type()
        self._validate_channel()

    def _validate_title(self) -> None:
        """Valida o título da notificação."""
        if not self.title or len(self.title.strip()) < 3:
            raise ValueError("Título deve ter pelo menos 3 caracteres")
        if len(self.title) > 100:
            raise ValueError("Título não pode ter mais de 100 caracteres")

    def _validate_message(self) -> None:
        """Valida a mensagem da notificação."""
        if not self.message or len(self.message.strip()) < 5:
            raise ValueError("Mensagem deve ter pelo menos 5 caracteres")
        if len(self.message) > 500:
            raise ValueError("Mensagem não pode ter mais de 500 caracteres")

    def _validate_notification_type(self) -> None:
        """Valida o tipo da notificação."""
        valid_types = [ntype.value for ntype in NotificationType]
        if self.notification_type not in valid_types:
            raise ValueError(f"Tipo deve ser um dos seguintes: {valid_types}")

    def _validate_channel(self) -> None:
        """Valida o canal da notificação."""
        valid_channels = [channel.value for channel in NotificationChannel]
        if self.channel not in valid_channels:
            raise ValueError(f"Canal deve ser um dos seguintes: {valid_channels}")

    def mark_as_read(self) -> None:
        """Marca a notificação como lida."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()

    def mark_as_sent(self) -> None:
        """Marca a notificação como enviada."""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = datetime.utcnow()

    def is_complaint_related(self) -> bool:
        """Verifica se a notificação está relacionada a uma reclamação."""
        return self.related_complaint_id is not None

    def is_email_notification(self) -> bool:
        """Verifica se é uma notificação por email."""
        return self.channel == NotificationChannel.EMAIL.value

    def is_whatsapp_notification(self) -> bool:
        """Verifica se é uma notificação por WhatsApp."""
        return self.channel == NotificationChannel.WHATSAPP.value

    def is_push_notification(self) -> bool:
        """Verifica se é uma notificação push."""
        return self.channel == NotificationChannel.PUSH.value

    def is_in_app_notification(self) -> bool:
        """Verifica se é uma notificação in-app."""
        return self.channel == NotificationChannel.IN_APP.value

    def can_be_resent(self) -> bool:
        """Verifica se a notificação pode ser reenviada."""
        return not self.is_sent or self.is_email_notification()

    def get_priority_score(self) -> int:
        """Retorna uma pontuação de prioridade para ordenação."""
        priority_map = {
            NotificationType.SYSTEM_ANNOUNCEMENT.value: 1,
            NotificationType.COMPLAINT_RESOLVED.value: 2,
            NotificationType.COMPLAINT_RESPONDED.value: 3,
            NotificationType.COMPLAINT_VOTED.value: 4,
            NotificationType.COMPLAINT_CREATED.value: 5
        }
        return priority_map.get(self.notification_type, 5)

    @classmethod
    def create_complaint_notification(
        cls,
        user_id: int,
        complaint_id: int,
        notification_type: str,
        channel: str,
        title: str,
        message: str
    ) -> 'Notification':
        """
        Factory method para criar notificações relacionadas a reclamações.
        
        Args:
            user_id: ID do usuário que receberá a notificação
            complaint_id: ID da reclamação relacionada
            notification_type: Tipo da notificação
            channel: Canal de envio
            title: Título da notificação
            message: Mensagem da notificação
            
        Returns:
            Nova instância de Notification
        """
        return cls(
            id=None,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            channel=channel,
            related_complaint_id=complaint_id,
            created_at=datetime.utcnow()
        )

    @classmethod
    def create_system_notification(
        cls,
        user_id: int,
        channel: str,
        title: str,
        message: str,
        metadata: Optional[str] = None
    ) -> 'Notification':
        """
        Factory method para criar notificações do sistema.
        
        Args:
            user_id: ID do usuário que receberá a notificação
            channel: Canal de envio
            title: Título da notificação
            message: Mensagem da notificação
            metadata: Metadados adicionais (opcional)
            
        Returns:
            Nova instância de Notification
        """
        return cls(
            id=None,
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT.value,
            channel=channel,
            metadata=metadata,
            created_at=datetime.utcnow()
        )

    def to_dict(self) -> dict:
        """Converte a entidade para um dicionário."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'channel': self.channel,
            'is_read': self.is_read,
            'is_sent': self.is_sent,
            'related_complaint_id': self.related_complaint_id,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'priority_score': self.get_priority_score()
        }

