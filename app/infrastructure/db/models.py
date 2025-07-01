"""
Modelos SQLAlchemy - Camada de Infraestrutura

Estes modelos são específicos do SQLAlchemy e representam a estrutura
das tabelas no banco de dados. Eles são separados das entidades de domínio
para manter a independência das regras de negócio.
"""

from datetime import datetime
from .database import db


class UserModel(db.Model):
    """Modelo SQLAlchemy para usuários."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='reclamante')
    city = db.Column(db.String(100), nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamentos
    complaints = db.relationship('ComplaintModel', foreign_keys='ComplaintModel.user_id', backref='user', lazy='dynamic')
    admin_complaints = db.relationship('ComplaintModel', foreign_keys='ComplaintModel.admin_user_id', backref='admin_user', lazy='dynamic')
    votes = db.relationship('VoteModel', backref='user', lazy='dynamic')
    notifications = db.relationship('NotificationModel', backref='user', lazy='dynamic')
    responses = db.relationship('ResponseModel', backref='admin_user', lazy='dynamic')

    def __repr__(self):
        return f'<UserModel {self.username} - {self.city}>'


class ComplaintModel(db.Model):
    """Modelo SQLAlchemy para reclamações."""
    
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    subcategory = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    image_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pendente', nullable=False, index=True)
    priority = db.Column(db.String(20), default='normal', nullable=False, index=True)
    tags = db.Column(db.String(500), nullable=True)
    admin_response = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    votes = db.relationship('VoteModel', backref='complaint', lazy='dynamic', cascade='all, delete-orphan')
    responses = db.relationship('ResponseModel', backref='complaint', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('NotificationModel', backref='complaint', lazy='dynamic')

    def __repr__(self):
        return f'<ComplaintModel {self.title[:30]}... - {self.status}>'


class VoteModel(db.Model):
    """Modelo SQLAlchemy para votos em reclamações."""
    
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraint para evitar votos duplicados
    __table_args__ = (
        db.UniqueConstraint('user_id', 'complaint_id', name='unique_user_complaint_vote'),
        db.Index('idx_vote_complaint', 'complaint_id'),
        db.Index('idx_vote_user', 'user_id')
    )

    def __repr__(self):
        return f'<VoteModel user_id={self.user_id} complaint_id={self.complaint_id}>'


class ResponseModel(db.Model):
    """Modelo SQLAlchemy para respostas de administradores."""
    
    __tablename__ = 'responses'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False, index=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ResponseModel complaint_id={self.complaint_id} admin_id={self.admin_user_id}>'


class NotificationModel(db.Model):
    """Modelo SQLAlchemy para notificações."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, index=True)
    channel = db.Column(db.String(20), nullable=False, index=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    is_sent = db.Column(db.Boolean, default=False, nullable=False, index=True)
    related_complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=True, index=True)
    metadata = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<NotificationModel {self.title[:30]}... - {self.notification_type}>'

