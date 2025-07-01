"""
Casos de Uso de Autenticação

Contém a lógica de aplicação para operações de autenticação,
incluindo registro, login e logout de usuários.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from ..domain.entities.user import User
from ..infrastructure.db.database import db, bcrypt
from ..infrastructure.db.models import UserModel


class RegisterUserUseCase:
    """Caso de uso para registro de novos usuários."""
    
    def execute(self, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa o registro de um novo usuário.
        
        Args:
            user_data: Dados do usuário para registro
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_usuario)
        """
        try:
            # Validar se username já existe
            if self._username_exists(user_data['username']):
                return False, "Nome de usuário já existe", None
            
            # Validar se email já existe
            if self._email_exists(user_data['email']):
                return False, "Email já está em uso", None
            
            # Validar se CPF já existe
            if self._cpf_exists(user_data['cpf']):
                return False, "CPF já está cadastrado", None
            
            # Criar entidade de domínio para validação
            user_entity = User(
                id=None,
                username=user_data['username'],
                email=user_data['email'],
                cpf=user_data['cpf'],
                full_name=user_data['full_name'],
                role=user_data.get('role', 'reclamante'),
                city=user_data['city'],
                phone=user_data.get('phone'),
                created_at=datetime.utcnow()
            )
            
            # Criar modelo para persistência
            user_model = UserModel(
                username=user_entity.username,
                email=user_entity.email,
                cpf=user_entity.cpf,
                password_hash=bcrypt.generate_password_hash(user_data['password']).decode('utf-8'),
                role=user_entity.role,
                city=user_entity.city,
                full_name=user_entity.full_name,
                phone=user_entity.phone
            )
            
            # Salvar no banco
            db.session.add(user_model)
            db.session.commit()
            
            # Converter para entidade para retorno
            user_entity.id = user_model.id
            user_entity.created_at = user_model.created_at
            
            return True, "Usuário registrado com sucesso", user_entity.to_dict()
            
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None
    
    def _username_exists(self, username: str) -> bool:
        """Verifica se o username já existe."""
        return UserModel.query.filter_by(username=username).first() is not None
    
    def _email_exists(self, email: str) -> bool:
        """Verifica se o email já existe."""
        return UserModel.query.filter_by(email=email).first() is not None
    
    def _cpf_exists(self, cpf: str) -> bool:
        """Verifica se o CPF já existe."""
        formatted_cpf = User._format_cpf(cpf)
        return UserModel.query.filter_by(cpf=formatted_cpf).first() is not None


class LoginUserUseCase:
    """Caso de uso para login de usuários."""
    
    def execute(self, login_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa o login de um usuário.
        
        Args:
            login_data: Dados de login (identifier e password)
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_resposta)
        """
        try:
            identifier = login_data['identifier']  # pode ser username, email ou CPF
            password = login_data['password']
            
            # Buscar usuário por username, email ou CPF
            user_model = self._find_user_by_identifier(identifier)
            
            if not user_model:
                return False, "Usuário não encontrado", None
            
            if not user_model.is_active:
                return False, "Conta desativada", None
            
            # Verificar senha
            if not bcrypt.check_password_hash(user_model.password_hash, password):
                return False, "Senha incorreta", None
            
            # Gerar token JWT
            access_token = create_access_token(identity=user_model.id)
            
            # Converter para entidade
            user_entity = self._model_to_entity(user_model)
            
            response_data = {
                'access_token': access_token,
                'user': user_entity.to_dict()
            }
            
            return True, "Login realizado com sucesso", response_data
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}", None
    
    def _find_user_by_identifier(self, identifier: str) -> Optional[UserModel]:
        """Busca usuário por username, email ou CPF."""
        # Tentar por username
        user = UserModel.query.filter_by(username=identifier).first()
        if user:
            return user
        
        # Tentar por email
        user = UserModel.query.filter_by(email=identifier).first()
        if user:
            return user
        
        # Tentar por CPF (formatado)
        formatted_cpf = User._format_cpf(identifier)
        user = UserModel.query.filter_by(cpf=formatted_cpf).first()
        return user
    
    def _model_to_entity(self, user_model: UserModel) -> User:
        """Converte modelo para entidade."""
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            cpf=user_model.cpf,
            full_name=user_model.full_name,
            role=user_model.role,
            city=user_model.city,
            phone=user_model.phone,
            profile_picture=user_model.profile_picture,
            bio=user_model.bio,
            is_active=user_model.is_active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )


class LogoutUserUseCase:
    """Caso de uso para logout de usuários."""
    
    def execute(self, user_id: int) -> Tuple[bool, str]:
        """
        Executa o logout de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        try:
            # Em uma implementação mais robusta, aqui poderíamos
            # invalidar o token JWT em uma blacklist
            # Por enquanto, apenas retornamos sucesso
            return True, "Logout realizado com sucesso"
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}"


class CheckUsernameAvailabilityUseCase:
    """Caso de uso para verificar disponibilidade de username."""
    
    def execute(self, username: str) -> Tuple[bool, str]:
        """
        Verifica se um username está disponível.
        
        Args:
            username: Username a ser verificado
            
        Returns:
            Tupla contendo (disponível, mensagem)
        """
        try:
            exists = UserModel.query.filter_by(username=username).first() is not None
            
            if exists:
                return False, "Nome de usuário já está em uso"
            else:
                return True, "Nome de usuário disponível"
                
        except Exception as e:
            return False, f"Erro interno: {str(e)}"


class CheckEmailAvailabilityUseCase:
    """Caso de uso para verificar disponibilidade de email."""
    
    def execute(self, email: str) -> Tuple[bool, str]:
        """
        Verifica se um email está disponível.
        
        Args:
            email: Email a ser verificado
            
        Returns:
            Tupla contendo (disponível, mensagem)
        """
        try:
            # Validar formato do email
            if not User.is_valid_email(email):
                return False, "Formato de email inválido"
            
            exists = UserModel.query.filter_by(email=email).first() is not None
            
            if exists:
                return False, "Email já está em uso"
            else:
                return True, "Email disponível"
                
        except Exception as e:
            return False, f"Erro interno: {str(e)}"

