from src.database import db, bcrypt
from datetime import datetime
import re

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='reclamante')  # 'reclamante' or 'responsavel'
    city = db.Column(db.String(100), nullable=False)  # cidade do usuário
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, email, cpf, password, role='reclamante', city='cuiaba', full_name='', phone=None):
        self.username = username
        self.email = email
        self.cpf = self.format_cpf(cpf)
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
        self.city = city.lower()
        self.full_name = full_name
        self.phone = phone

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def format_cpf(cpf):
        # Remove caracteres não numéricos
        cpf_numbers = re.sub(r'\D', '', cpf)
        # Formata como XXX.XXX.XXX-XX
        if len(cpf_numbers) == 11:
            return f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"
        return cpf_numbers

    @staticmethod
    def validate_cpf(cpf):
        # Remove caracteres não numéricos
        cpf_numbers = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf_numbers) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
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
        
        if int(cpf_numbers[10]) != digit2:
            return False
        
        return True

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'cpf': self.cpf,
            'role': self.role,
            'city': self.city,
            'full_name': self.full_name,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username} - {self.city}>'

