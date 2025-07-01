import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from src.database import db
from src.models.notification import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize notification service with Flask app"""
        self.smtp_server = app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = app.config.get('SMTP_PORT', 587)
        self.smtp_username = app.config.get('SMTP_USERNAME', '')
        self.smtp_password = app.config.get('SMTP_PASSWORD', '')
        self.from_email = app.config.get('FROM_EMAIL', 'noreply@deuruimcidadao.com.br')
        
        # WhatsApp API configuration (using a mock service for demo)
        self.whatsapp_api_url = app.config.get('WHATSAPP_API_URL', 'https://api.whatsapp.mock.com')
        self.whatsapp_token = app.config.get('WHATSAPP_TOKEN', 'demo_token')
        
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add plain text part
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # For demo purposes, we'll just log the email instead of actually sending
            logger.info(f"EMAIL SENT TO: {to_email}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"BODY: {body}")
            
            # In production, uncomment this to actually send emails:
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.smtp_username, self.smtp_password)
            #     server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp notification"""
        try:
            # Format phone number (remove non-digits and add country code if needed)
            phone = ''.join(filter(str.isdigit, phone_number))
            if not phone.startswith('55'):
                phone = '55' + phone
            
            # For demo purposes, we'll just log the WhatsApp message
            logger.info(f"WHATSAPP SENT TO: +{phone}")
            logger.info(f"MESSAGE: {message}")
            
            # In production, uncomment this to actually send WhatsApp messages:
            # payload = {
            #     'phone': phone,
            #     'message': message,
            #     'token': self.whatsapp_token
            # }
            # response = requests.post(self.whatsapp_api_url, json=payload, timeout=10)
            # return response.status_code == 200
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {phone_number}: {str(e)}")
            return False
    
    def send_complaint_notification(self, user_id: int, complaint_id: int, notification_type: str, 
                                  extra_data: Dict = None) -> bool:
        """Send notification about complaint status change"""
        try:
            from src.models.user import User
            from src.models.complaint import Complaint
            
            user = User.query.get(user_id)
            complaint = Complaint.query.get(complaint_id)
            
            if not user or not complaint:
                logger.error(f"User {user_id} or complaint {complaint_id} not found")
                return False
            
            # Generate notification content based on type
            subject, email_body, whatsapp_message = self._generate_notification_content(
                notification_type, user, complaint, extra_data
            )
            
            # Send email if user has email notifications enabled
            email_sent = False
            if user.email_notifications and user.email:
                email_sent = self.send_email(user.email, subject, email_body)
            
            # Send WhatsApp if user has WhatsApp notifications enabled
            whatsapp_sent = False
            if user.whatsapp_notifications and user.phone:
                whatsapp_sent = self.send_whatsapp(user.phone, whatsapp_message)
            
            # Save notification to database
            notification = Notification(
                user_id=user_id,
                complaint_id=complaint_id,
                type=notification_type,
                title=subject,
                message=email_body,
                email_sent=email_sent,
                whatsapp_sent=whatsapp_sent,
                extra_data=extra_data or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return email_sent or whatsapp_sent
            
        except Exception as e:
            logger.error(f"Error sending complaint notification: {str(e)}")
            return False
    
    def _generate_notification_content(self, notification_type: str, user, complaint, extra_data: Dict = None):
        """Generate notification content based on type"""
        extra_data = extra_data or {}
        
        templates = {
            'complaint_created': {
                'subject': f'Reclamação #{complaint.id} registrada com sucesso',
                'email_body': f'''Olá {user.full_name},

Sua reclamação foi registrada com sucesso no sistema deuruimcidadao!

Detalhes da reclamação:
- ID: #{complaint.id}
- Título: {complaint.title}
- Categoria: {complaint.category}
- Status: {complaint.status}
- Data: {complaint.created_at.strftime('%d/%m/%Y às %H:%M')}

Você receberá atualizações sobre o andamento da sua reclamação.

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'🏛️ *deuruimcidadao*\n\nSua reclamação #{complaint.id} foi registrada!\n\n📋 *{complaint.title}*\n📍 {complaint.location}\n⏰ Status: {complaint.status}\n\nVocê receberá atualizações sobre o andamento.'
            },
            
            'status_updated': {
                'subject': f'Reclamação #{complaint.id} - Status atualizado',
                'email_body': f'''Olá {user.full_name},

Sua reclamação teve o status atualizado!

Detalhes:
- ID: #{complaint.id}
- Título: {complaint.title}
- Novo Status: {complaint.status}
- Data da atualização: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

{extra_data.get('admin_message', '')}

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'🏛️ *deuruimcidadao*\n\n📢 Atualização da reclamação #{complaint.id}\n\n📋 *{complaint.title}*\n🔄 Novo status: *{complaint.status}*\n\n{extra_data.get("admin_message", "")}'
            },
            
            'complaint_resolved': {
                'subject': f'Reclamação #{complaint.id} foi resolvida!',
                'email_body': f'''Olá {user.full_name},

Temos uma ótima notícia! Sua reclamação foi resolvida.

Detalhes:
- ID: #{complaint.id}
- Título: {complaint.title}
- Status: Resolvida
- Data da resolução: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

{extra_data.get('resolution_message', '')}

Por favor, avalie o atendimento recebido acessando sua conta no deuruimcidadao.

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'🎉 *deuruimcidadao*\n\n✅ Sua reclamação #{complaint.id} foi RESOLVIDA!\n\n📋 *{complaint.title}*\n📍 {complaint.location}\n\nPor favor, avalie o atendimento no app!'
            },
            
            'new_response': {
                'subject': f'Nova resposta na reclamação #{complaint.id}',
                'email_body': f'''Olá {user.full_name},

Você recebeu uma nova resposta na sua reclamação.

Detalhes:
- ID: #{complaint.id}
- Título: {complaint.title}
- Resposta de: {extra_data.get('responder_name', 'Administração')}
- Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}

Resposta:
{extra_data.get('response_message', '')}

Acesse sua conta para ver mais detalhes.

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'💬 *deuruimcidadao*\n\nNova resposta na reclamação #{complaint.id}\n\n📋 *{complaint.title}*\n👤 {extra_data.get("responder_name", "Administração")}\n\n"{extra_data.get("response_message", "")[:100]}..."\n\nVeja mais no app!'
            }
        }
        
        template = templates.get(notification_type, templates['complaint_created'])
        return template['subject'], template['email_body'], template['whatsapp']
    
    def send_bulk_notifications(self, user_ids: List[int], notification_type: str, 
                              extra_data: Dict = None) -> Dict[str, int]:
        """Send bulk notifications to multiple users"""
        results = {'sent': 0, 'failed': 0}
        
        for user_id in user_ids:
            try:
                success = self.send_system_notification(user_id, notification_type, extra_data)
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error sending bulk notification to user {user_id}: {str(e)}")
                results['failed'] += 1
        
        return results
    
    def send_system_notification(self, user_id: int, notification_type: str, 
                               extra_data: Dict = None) -> bool:
        """Send system-wide notification (not related to specific complaint)"""
        try:
            from src.models.user import User
            
            user = User.query.get(user_id)
            if not user:
                return False
            
            # Generate system notification content
            subject, email_body, whatsapp_message = self._generate_system_notification_content(
                notification_type, user, extra_data
            )
            
            # Send notifications
            email_sent = False
            if user.email_notifications and user.email:
                email_sent = self.send_email(user.email, subject, email_body)
            
            whatsapp_sent = False
            if user.whatsapp_notifications and user.phone:
                whatsapp_sent = self.send_whatsapp(user.phone, whatsapp_message)
            
            # Save to database
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=subject,
                message=email_body,
                email_sent=email_sent,
                whatsapp_sent=whatsapp_sent,
                extra_data=extra_data or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            return email_sent or whatsapp_sent
            
        except Exception as e:
            logger.error(f"Error sending system notification: {str(e)}")
            return False
    
    def _generate_system_notification_content(self, notification_type: str, user, extra_data: Dict = None):
        """Generate system notification content"""
        extra_data = extra_data or {}
        
        templates = {
            'welcome': {
                'subject': 'Bem-vindo ao deuruimcidadao!',
                'email_body': f'''Olá {user.full_name},

Bem-vindo ao deuruimcidadao - a plataforma que conecta você à sua cidade!

Com o deuruimcidadao você pode:
- Registrar reclamações sobre problemas urbanos
- Acompanhar o andamento das suas solicitações
- Votar em reclamações de outros cidadãos
- Contribuir para uma cidade melhor

Sua voz importa! Juntos podemos fazer a diferença.

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'🏛️ *Bem-vindo ao deuruimcidadao!*\n\nOlá {user.full_name}! 👋\n\nAgora você pode registrar reclamações, acompanhar soluções e contribuir para uma cidade melhor!\n\nSua voz importa! 🗣️'
            },
            
            'monthly_report': {
                'subject': 'Relatório mensal - deuruimcidadao',
                'email_body': f'''Olá {user.full_name},

Aqui está o resumo das suas atividades no último mês:

- Reclamações registradas: {extra_data.get('complaints_count', 0)}
- Votos dados: {extra_data.get('votes_count', 0)}
- Reclamações resolvidas: {extra_data.get('resolved_count', 0)}
- Pontos XP ganhos: {extra_data.get('xp_gained', 0)}

Continue contribuindo para uma cidade melhor!

Atenciosamente,
Equipe deuruimcidadao''',
                'whatsapp': f'📊 *Relatório Mensal*\n\n{user.full_name}, veja suas atividades:\n\n📝 {extra_data.get("complaints_count", 0)} reclamações\n👍 {extra_data.get("votes_count", 0)} votos\n✅ {extra_data.get("resolved_count", 0)} resolvidas\n⭐ {extra_data.get("xp_gained", 0)} XP\n\nContinue contribuindo! 🏆'
            }
        }
        
        template = templates.get(notification_type, templates['welcome'])
        return template['subject'], template['email_body'], template['whatsapp']
    
    def get_user_notifications(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get notifications for a user"""
        notifications = Notification.query.filter_by(user_id=user_id)\
                                        .order_by(Notification.created_at.desc())\
                                        .limit(limit)\
                                        .offset(offset)\
                                        .all()
        
        return [notification.to_dict() for notification in notifications]
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        try:
            notification = Notification.query.filter_by(
                id=notification_id, 
                user_id=user_id
            ).first()
            
            if notification:
                notification.read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for user"""
        return Notification.query.filter_by(user_id=user_id, read=False).count()

# Global notification service instance
notification_service = NotificationService()

