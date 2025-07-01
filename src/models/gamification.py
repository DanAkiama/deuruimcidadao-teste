from src.database import db
from datetime import datetime

class UserPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)  # Total histórico
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='points_record')

    def add_points(self, points, action):
        """Adiciona pontos e registra a ação"""
        self.points += points
        self.total_points += points
        self.updated_at = datetime.utcnow()
        
        # Calcular novo nível (a cada 100 pontos = 1 nível)
        new_level = (self.total_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
            # Criar badge de nível se necessário
            Badge.award_level_badge(self.user_id, new_level)
        
        # Registrar histórico
        PointHistory.create_record(self.user_id, points, action)
        
        db.session.commit()
        return self.points

    def get_level_progress(self):
        """Retorna progresso para o próximo nível"""
        current_level_points = (self.level - 1) * 100
        next_level_points = self.level * 100
        progress = self.total_points - current_level_points
        return {
            'current_level': self.level,
            'progress': progress,
            'points_to_next': next_level_points - self.total_points,
            'percentage': (progress / 100) * 100
        }

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'points': self.points,
            'total_points': self.total_points,
            'level': self.level,
            'level_progress': self.get_level_progress()
        }


class PointHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='point_history')

    @staticmethod
    def create_record(user_id, points, action):
        record = PointHistory(
            user_id=user_id,
            points=points,
            action=action
        )
        db.session.add(record)
        return record

    def to_dict(self):
        return {
            'id': self.id,
            'points': self.points,
            'action': self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'level', 'activity', 'special'
    requirement = db.Column(db.Integer, nullable=True)  # Para badges baseadas em números
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def award_level_badge(user_id, level):
        """Concede badge de nível"""
        level_badges = {
            5: {'name': 'Cidadão Iniciante', 'icon': 'star'},
            10: {'name': 'Cidadão Ativo', 'icon': 'star-fill'},
            25: {'name': 'Cidadão Engajado', 'icon': 'award'},
            50: {'name': 'Cidadão Exemplar', 'icon': 'trophy'},
            100: {'name': 'Guardião da Cidade', 'icon': 'crown'}
        }
        
        if level in level_badges:
            badge_info = level_badges[level]
            badge = Badge.query.filter_by(name=badge_info['name']).first()
            if badge:
                UserBadge.award_badge(user_id, badge.id)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'requirement': self.requirement
        }


class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='user_badges')
    badge = db.relationship('Badge', backref='badge_users')
    
    # Constraint para evitar badges duplicadas
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)

    @staticmethod
    def award_badge(user_id, badge_id):
        """Concede uma badge para um usuário"""
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first()
        if not existing:
            user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
            db.session.add(user_badge)
            db.session.commit()
            return user_badge
        return existing

    def to_dict(self):
        return {
            'id': self.id,
            'badge': self.badge.to_dict(),
            'earned_at': self.earned_at.isoformat() if self.earned_at else None
        }


class CityRanking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    rank_position = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=False)  # Mês do ranking
    year = db.Column(db.Integer, nullable=False)   # Ano do ranking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    user = db.relationship('User', backref='city_rankings')
    
    # Constraint para evitar duplicatas
    __table_args__ = (db.UniqueConstraint('city', 'user_id', 'month', 'year', name='unique_city_user_month'),)

    @staticmethod
    def update_monthly_ranking(city):
        """Atualiza o ranking mensal de uma cidade"""
        from datetime import datetime
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Buscar usuários da cidade com mais pontos no mês
        users_points = db.session.query(
            User.id,
            func.sum(PointHistory.points).label('total_points')
        ).join(PointHistory).filter(
            User.city == city.lower(),
            func.extract('month', PointHistory.created_at) == current_month,
            func.extract('year', PointHistory.created_at) == current_year
        ).group_by(User.id).order_by(desc('total_points')).all()
        
        # Atualizar ranking
        for position, (user_id, points) in enumerate(users_points, 1):
            ranking = CityRanking.query.filter_by(
                city=city.lower(),
                user_id=user_id,
                month=current_month,
                year=current_year
            ).first()
            
            if ranking:
                ranking.points = points
                ranking.rank_position = position
                ranking.updated_at = datetime.utcnow()
            else:
                ranking = CityRanking(
                    city=city.lower(),
                    user_id=user_id,
                    points=points,
                    rank_position=position,
                    month=current_month,
                    year=current_year
                )
                db.session.add(ranking)
        
        db.session.commit()

    def to_dict(self):
        return {
            'city': self.city,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            },
            'points': self.points,
            'rank_position': self.rank_position,
            'month': self.month,
            'year': self.year
        }


# Adicionar métodos ao modelo User para gamificação
def add_points_to_user(self, points, action):
    """Adiciona pontos ao usuário"""
    user_points = UserPoints.query.filter_by(user_id=self.id).first()
    if not user_points:
        user_points = UserPoints(user_id=self.id)
        db.session.add(user_points)
        db.session.commit()
    
    return user_points.add_points(points, action)

def get_user_badges(self):
    """Retorna badges do usuário"""
    return [ub.to_dict() for ub in self.user_badges]

def get_user_ranking(self, city=None):
    """Retorna posição no ranking da cidade"""
    target_city = city or self.city
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    ranking = CityRanking.query.filter_by(
        city=target_city.lower(),
        user_id=self.id,
        month=current_month,
        year=current_year
    ).first()
    
    return ranking.to_dict() if ranking else None

# Adicionar métodos ao modelo User
from src.models.user import User
User.add_points = add_points_to_user
User.get_badges = get_user_badges
User.get_ranking = get_user_ranking

