"""
Entidade Complaint - Representa uma reclamação no sistema

Esta entidade contém as regras de negócio puras relacionadas às reclamações,
sem dependências de frameworks ou infraestrutura.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ComplaintStatus(Enum):
    """Status possíveis para uma reclamação."""
    PENDENTE = "pendente"
    RESPONDIDA = "respondida"
    RESOLVIDA = "resolvida"


class ComplaintPriority(Enum):
    """Prioridades possíveis para uma reclamação."""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class ComplaintCategory(Enum):
    """Categorias possíveis para uma reclamação."""
    BURACOS = "buracos"
    ILUMINACAO = "iluminacao"
    LIMPEZA = "limpeza"
    TRANSITO = "transito"
    SEGURANCA = "seguranca"
    OUTROS = "outros"


@dataclass
class Complaint:
    """
    Entidade que representa uma reclamação no sistema.
    
    Contém as regras de negócio puras relacionadas às reclamações,
    incluindo validações e lógicas específicas do domínio.
    """
    
    id: Optional[int]
    title: str
    description: str
    category: str
    user_id: int
    city: str
    subcategory: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_path: Optional[str] = None
    status: str = ComplaintStatus.PENDENTE.value
    priority: str = ComplaintPriority.NORMAL.value
    tags: Optional[str] = None
    admin_response: Optional[str] = None
    admin_user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    vote_count: int = 0

    def __post_init__(self):
        """Validações executadas após a criação do objeto."""
        self._validate_title()
        self._validate_description()
        self._validate_category()
        self._validate_status()
        self._validate_priority()
        self._validate_coordinates()

    def _validate_title(self) -> None:
        """Valida o título da reclamação."""
        if not self.title or len(self.title.strip()) < 5:
            raise ValueError("Título deve ter pelo menos 5 caracteres")
        if len(self.title) > 200:
            raise ValueError("Título não pode ter mais de 200 caracteres")

    def _validate_description(self) -> None:
        """Valida a descrição da reclamação."""
        if not self.description or len(self.description.strip()) < 10:
            raise ValueError("Descrição deve ter pelo menos 10 caracteres")

    def _validate_category(self) -> None:
        """Valida a categoria da reclamação."""
        valid_categories = [cat.value for cat in ComplaintCategory]
        if self.category not in valid_categories:
            raise ValueError(f"Categoria deve ser uma das seguintes: {valid_categories}")

    def _validate_status(self) -> None:
        """Valida o status da reclamação."""
        valid_statuses = [status.value for status in ComplaintStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"Status deve ser um dos seguintes: {valid_statuses}")

    def _validate_priority(self) -> None:
        """Valida a prioridade da reclamação."""
        valid_priorities = [priority.value for priority in ComplaintPriority]
        if self.priority not in valid_priorities:
            raise ValueError(f"Prioridade deve ser uma das seguintes: {valid_priorities}")

    def _validate_coordinates(self) -> None:
        """Valida as coordenadas geográficas."""
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                raise ValueError("Latitude deve estar entre -90 e 90")
        
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                raise ValueError("Longitude deve estar entre -180 e 180")

    def is_pending(self) -> bool:
        """Verifica se a reclamação está pendente."""
        return self.status == ComplaintStatus.PENDENTE.value

    def is_responded(self) -> bool:
        """Verifica se a reclamação foi respondida."""
        return self.status == ComplaintStatus.RESPONDIDA.value

    def is_resolved(self) -> bool:
        """Verifica se a reclamação foi resolvida."""
        return self.status == ComplaintStatus.RESOLVIDA.value

    def is_high_priority(self) -> bool:
        """Verifica se a reclamação tem prioridade alta ou urgente."""
        return self.priority in [ComplaintPriority.ALTA.value, ComplaintPriority.URGENTE.value]

    def has_location(self) -> bool:
        """Verifica se a reclamação possui localização definida."""
        return self.latitude is not None and self.longitude is not None

    def has_image(self) -> bool:
        """Verifica se a reclamação possui imagem anexada."""
        return self.image_path is not None and self.image_path.strip() != ""

    def can_be_edited_by_user(self, user_id: int) -> bool:
        """Verifica se a reclamação pode ser editada pelo usuário."""
        return self.user_id == user_id and self.is_pending()

    def can_be_managed_by_admin(self) -> bool:
        """Verifica se a reclamação pode ser gerenciada por um administrador."""
        return not self.is_resolved()

    def mark_as_responded(self, admin_user_id: int, response: str) -> None:
        """Marca a reclamação como respondida."""
        if not response or len(response.strip()) < 10:
            raise ValueError("Resposta deve ter pelo menos 10 caracteres")
        
        self.status = ComplaintStatus.RESPONDIDA.value
        self.admin_response = response
        self.admin_user_id = admin_user_id
        self.updated_at = datetime.utcnow()

    def mark_as_resolved(self, admin_user_id: int) -> None:
        """Marca a reclamação como resolvida."""
        self.status = ComplaintStatus.RESOLVIDA.value
        self.admin_user_id = admin_user_id
        self.resolved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_vote(self) -> None:
        """Adiciona um voto à reclamação."""
        self.vote_count += 1

    def remove_vote(self) -> None:
        """Remove um voto da reclamação."""
        if self.vote_count > 0:
            self.vote_count -= 1

    def get_tags_list(self) -> List[str]:
        """Retorna as tags como uma lista."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def set_tags_from_list(self, tags_list: List[str]) -> None:
        """Define as tags a partir de uma lista."""
        self.tags = ', '.join(tags_list) if tags_list else None

    def to_dict(self) -> dict:
        """Converte a entidade para um dicionário."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'image_path': self.image_path,
            'status': self.status,
            'priority': self.priority,
            'tags': self.tags,
            'admin_response': self.admin_response,
            'user_id': self.user_id,
            'admin_user_id': self.admin_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'vote_count': self.vote_count,
            'has_location': self.has_location(),
            'has_image': self.has_image(),
            'is_high_priority': self.is_high_priority()
        }

