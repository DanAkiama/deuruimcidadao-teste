from src.database import db
from datetime import datetime

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # 'complaint_created', 'status_updated', 'response_added'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_email = db.Column(db.Boolean, default=False)
    sent_whatsapp = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='notifications')
    complaint = db.relationship('Complaint', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'complaint_id': self.complaint_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'sent_email': self.sent_email,
            'sent_whatsapp': self.sent_whatsapp,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()

    @staticmethod
    def create_notification(user_id, type, title, message, complaint_id=None):
        notification = Notification(
            user_id=user_id,
            complaint_id=complaint_id,
            type=type,
            title=title,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def __repr__(self):
        return f'<Notification {self.id}: {self.type} for User {self.user_id}>'

