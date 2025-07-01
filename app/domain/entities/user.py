"""
Entidade User - Representa um usuário do sistema

Esta entidade contém as regras de negócio puras relacionadas aos usuários,
sem dependências de frameworks ou infraestrutura.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class User:
    """
    Entidade que representa um usuário do sistema.
    
    Contém as regras de negócio puras relacionadas aos usuários,
    incluindo validações de CPF, email e outras regras específicas.
    """
    
    id: Optional[int]
    username: str
    email: str
    cpf: str
    full_name: str
    role: str  # 'reclamante' ou 'responsavel'
    city: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validações executadas após a criação do objeto."""
        self._validate_email()
        self._validate_cpf()
        self._validate_role()
        self.cpf = self._format_cpf(self.cpf)
        self.city = self.city.lower()

    def _validate_email(self) -> None:
        """Valida o formato do email."""
        if not self.is_valid_email(self.email):
            raise ValueError("Email inválido")

    def _validate_cpf(self) -> None:
        """Valida o CPF."""
        if not self.is_valid_cpf(self.cpf):
            raise ValueError("CPF inválido")

    def _validate_role(self) -> None:
        """Valida o tipo de usuário."""
        valid_roles = ['reclamante', 'responsavel']
        if self.role not in valid_roles:
            raise ValueError(f"Role deve ser um dos seguintes: {valid_roles}")

    @staticmethod
    def _format_cpf(cpf: str) -> str:
        """Formata o CPF no padrão XXX.XXX.XXX-XX."""
        cpf_numbers = re.sub(r'\D', '', cpf)
        if len(cpf_numbers) == 11:
            return f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"
        return cpf_numbers

    @staticmethod
    def is_valid_cpf(cpf: str) -> bool:
        """
        Valida um CPF brasileiro.
        
        Args:
            cpf: CPF a ser validado
            
        Returns:
            True se o CPF for válido, False caso contrário
        """
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        if len(cpf_numbers) != 11:
            return False
        
        if cpf_numbers == cpf_numbers[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        sum1 = sum(int(cpf_numbers[i]) * (10 - i) for i in range(9))
        digit1 = (sum1 * 10) % 11
        if digit1 == 10:
            digit1 = 0
        
        if int(cpf_numbers[9]) != digit1:
            return False
        
        # Validação do segundo dígito verificador
        sum2 = sum(int(cpf_numbers[i]) * (11 - i) for i in range(10))
        digit2 = (sum2 * 10) % 11
        if digit2 == 10:
            digit2 = 0
        
        return int(cpf_numbers[10]) == digit2

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Valida o formato de um email.
        
        Args:
            email: Email a ser validado
            
        Returns:
            True se o email for válido, False caso contrário
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def is_reclamante(self) -> bool:
        """Verifica se o usuário é um reclamante."""
        return self.role == 'reclamante'

    def is_responsavel(self) -> bool:
        """Verifica se o usuário é um responsável."""
        return self.role == 'responsavel'

    def can_manage_complaints(self) -> bool:
        """Verifica se o usuário pode gerenciar reclamações."""
        return self.is_responsavel()

    def can_create_complaints(self) -> bool:
        """Verifica se o usuário pode criar reclamações."""
        return self.is_active

    def to_dict(self) -> dict:
        """Converte a entidade para um dicionário."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'cpf': self.cpf,
            'full_name': self.full_name,
            'role': self.role,
            'city': self.city,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

