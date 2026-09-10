from datetime import datetime
from extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), default='Cash on Delivery')
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy='joined', cascade='all, delete-orphan')

    STATUS_FLOW = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered']

    def status_index(self):
        try:
            return self.STATUS_FLOW.index(self.status)
        except ValueError:
            return -1

    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def subtotal(self):
        return self.quantity * self.price

    def __repr__(self):
        return f'<OrderItem order={self.order_id} product={self.product_id}>'
