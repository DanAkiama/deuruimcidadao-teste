"""
Casos de Uso de Usuário

Contém a lógica de aplicação para operações relacionadas ao perfil do usuário,
incluindo atualização de dados e troca de senha.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime

from ..domain.entities.user import User
from ..infrastructure.db.database import db, bcrypt
from ..infrastructure.db.models import UserModel


class UpdateUserProfileUseCase:
    """Caso de uso para atualização do perfil do usuário."""
    
    def execute(self, user_id: int, profile_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa a atualização do perfil de um usuário.
        
        Args:
            user_id: ID do usuário
            profile_data: Dados para atualização
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_usuario)
        """
        try:
            # Buscar usuário
            user_model = UserModel.query.get(user_id)
            if not user_model:
                return False, "Usuário não encontrado", None
            
            # Campos que podem ser atualizados
            allowed_fields = ['full_name', 'phone', 'bio', 'city']
            
            # Validar email se fornecido
            if 'email' in profile_data:
                new_email = profile_data['email']
                if new_email != user_model.email:
                    if not User.is_valid_email(new_email):
                        return False, "Email inválido", None
                    
                    # Verificar se email já existe
                    existing_user = UserModel.query.filter_by(email=new_email).first()
                    if existing_user and existing_user.id != user_id:
                        return False, "Email já está em uso", None
                    
                    user_model.email = new_email
            
            # Atualizar campos permitidos
            for field in allowed_fields:
                if field in profile_data:
                    setattr(user_model, field, profile_data[field])
            
            user_model.updated_at = datetime.utcnow()
            
            # Validar através da entidade
            user_entity = self._model_to_entity(user_model)
            
            # Salvar no banco
            db.session.commit()
            
            return True, "Perfil atualizado com sucesso", user_entity.to_dict()
            
        except ValueError as e:
            db.session.rollback()
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None
    
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


class ChangePasswordUseCase:
    """Caso de uso para troca de senha."""
    
    def execute(self, user_id: int, password_data: Dict) -> Tuple[bool, str]:
        """
        Executa a troca de senha de um usuário.
        
        Args:
            user_id: ID do usuário
            password_data: Dados da senha (current_password, new_password)
            
        Returns:
            Tupla contendo (sucesso, mensagem)
        """
        try:
            # Buscar usuário
            user_model = UserModel.query.get(user_id)
            if not user_model:
                return False, "Usuário não encontrado"
            
            current_password = password_data['current_password']
            new_password = password_data['new_password']
            
            # Verificar senha atual
            if not bcrypt.check_password_hash(user_model.password_hash, current_password):
                return False, "Senha atual incorreta"
            
            # Validar nova senha
            if len(new_password) < 6:
                return False, "Nova senha deve ter pelo menos 6 caracteres"
            
            if new_password == current_password:
                return False, "A nova senha deve ser diferente da atual"
            
            # Atualizar senha
            user_model.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user_model.updated_at = datetime.utcnow()
            
            # Salvar no banco
            db.session.commit()
            
            return True, "Senha alterada com sucesso"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}"


class GetUserProfileUseCase:
    """Caso de uso para obter perfil do usuário."""
    
    def execute(self, user_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Executa a busca do perfil de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Tupla contendo (sucesso, mensagem, dados_usuario)
        """
        try:
            # Buscar usuário
            user_model = UserModel.query.get(user_id)
            if not user_model:
                return False, "Usuário não encontrado", None
            
            # Converter para entidade
            user_entity = self._model_to_entity(user_model)
            
            # Adicionar estatísticas
            user_data = user_entity.to_dict()
            user_data['statistics'] = self._get_user_statistics(user_id)
            
            return True, "Perfil encontrado", user_data
            
        except Exception as e:
            return False, f"Erro interno: {str(e)}", None
    
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
    
    def _get_user_statistics(self, user_id: int) -> Dict:
        """Obtém estatísticas do usuário."""
        from ..infrastructure.db.models import ComplaintModel, VoteModel
        
        # Contar reclamações do usuário
        complaints_count = ComplaintModel.query.filter_by(user_id=user_id).count()
        
        # Contar reclamações resolvidas
        resolved_count = ComplaintModel.query.filter_by(
            user_id=user_id, 
            status='resolvida'
        ).count()
        
        # Contar votos dados pelo usuário
        votes_given = VoteModel.query.filter_by(user_id=user_id).count()
        
        # Contar votos recebidos nas reclamações do usuário
        votes_received = db.session.query(VoteModel).join(
            ComplaintModel, VoteModel.complaint_id == ComplaintModel.id
        ).filter(ComplaintModel.user_id == user_id).count()
        
        return {
            'complaints_count': complaints_count,
            'resolved_count': resolved_count,
            'votes_given': votes_given,
            'votes_received': votes_received
        }


class UploadProfilePictureUseCase:
    """Caso de uso para upload de foto de perfil."""
    
    def execute(self, user_id: int, file_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Executa o upload da foto de perfil.
        
        Args:
            user_id: ID do usuário
            file_path: Caminho do arquivo da foto
            
        Returns:
            Tupla contendo (sucesso, mensagem, caminho_arquivo)
        """
        try:
            # Buscar usuário
            user_model = UserModel.query.get(user_id)
            if not user_model:
                return False, "Usuário não encontrado", None
            
            # Validar extensão do arquivo
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = file_path.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                return False, "Formato de arquivo não permitido", None
            
            # Atualizar caminho da foto
            user_model.profile_picture = file_path
            user_model.updated_at = datetime.utcnow()
            
            # Salvar no banco
            db.session.commit()
            
            return True, "Foto de perfil atualizada com sucesso", file_path
            
        except Exception as e:
            db.session.rollback()
            return False, f"Erro interno: {str(e)}", None

