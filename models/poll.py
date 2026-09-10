from datetime import datetime
from extensions import db


class Poll(db.Model):
    __tablename__ = 'polls'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    votes = db.relationship('PollVote', backref='poll', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Poll {self.title}>'


class PollVote(db.Model):
    __tablename__ = 'poll_votes'

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rank = db.Column(db.Integer, nullable=False)  # 1, 2, or 3
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('poll_votes', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('poll_votes', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('poll_id', 'user_id', 'rank', name='unique_poll_user_rank'),
        db.UniqueConstraint('poll_id', 'user_id', 'product_id', name='unique_poll_user_product'),
    )

    def __repr__(self):
        return f'<PollVote user={self.user_id} product={self.product_id} rank={self.rank}>'


class CustomOrder(db.Model):
    __tablename__ = 'custom_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    base_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    cake_message = db.Column(db.String(100))
    size = db.Column(db.String(50), default='Regular')  # Regular, Medium, Large
    flavour_notes = db.Column(db.String(200))
    special_instructions = db.Column(db.Text)
    delivery_date = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Pending')
    estimated_price = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('custom_orders', lazy='dynamic'))
    base_product = db.relationship('Product', backref=db.backref('custom_orders', lazy='dynamic'))

    def __repr__(self):
        return f'<CustomOrder {self.id} by user={self.user_id}>'
