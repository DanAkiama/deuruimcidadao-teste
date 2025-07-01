from src.database import db
from datetime import datetime

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subcategory = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='pendente')  # pendente, respondida, resolvido
    priority = db.Column(db.String(20), default='normal')  # baixa, normal, alta, urgente
    tags = db.Column(db.String(500), nullable=True)
    admin_response = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos com foreign_keys especificadas
    user = db.relationship('User', foreign_keys=[user_id], backref='user_complaints')
    admin_user = db.relationship('User', foreign_keys=[admin_user_id], backref='admin_complaints')
    
    def get_vote_count(self):
        """Retorna o número de votos da reclamação"""
        return Vote.query.filter_by(complaint_id=self.id).count()
    
    def get_user_vote(self, user_id):
        """Verifica se um usuário votou nesta reclamação"""
        return Vote.query.filter_by(complaint_id=self.id, user_id=user_id).first() is not None
    
    def to_dict(self):
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
            'vote_count': self.get_vote_count()
        }


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='votes')
    complaint = db.relationship('Complaint', backref='votes')
    
    # Constraint para evitar votos duplicados
    __table_args__ = (db.UniqueConstraint('user_id', 'complaint_id', name='unique_user_complaint_vote'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'complaint_id': self.complaint_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    complaint = db.relationship('Complaint', backref='responses')
    admin_user = db.relationship('User', backref='admin_responses')
    
    def to_dict(self):
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'admin_user_id': self.admin_user_id,
            'message': self.message,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'admin_user': {
                'id': self.admin_user.id,
                'username': self.admin_user.username,
                'full_name': self.admin_user.full_name
            } if self.admin_user else None
        }

