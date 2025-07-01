"""
Use Cases Layer - Camada de Casos de Uso

Esta camada contém a lógica de aplicação e orquestra as operações
entre as entidades de domínio e a infraestrutura.

Contém:
- Casos de uso específicos da aplicação
- Orquestração de operações de negócio
- Validações de entrada
- Coordenação entre diferentes serviços
"""

from .auth_usecases import RegisterUserUseCase, LoginUserUseCase, LogoutUserUseCase
from .complaint_usecases import CreateComplaintUseCase, UpdateComplaintUseCase, VoteComplaintUseCase
from .user_usecases import UpdateUserProfileUseCase, ChangePasswordUseCase
from .notification_usecases import SendNotificationUseCase, MarkNotificationAsReadUseCase

__all__ = [
    'RegisterUserUseCase',
    'LoginUserUseCase', 
    'LogoutUserUseCase',
    'CreateComplaintUseCase',
    'UpdateComplaintUseCase',
    'VoteComplaintUseCase',
    'UpdateUserProfileUseCase',
    'ChangePasswordUseCase',
    'SendNotificationUseCase',
    'MarkNotificationAsReadUseCase'
]

