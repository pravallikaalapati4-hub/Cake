from datetime import datetime
from extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), default='placeholder.jpg')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    ingredients = db.Column(db.Text)
    stock = db.Column(db.Integer, default=50)
    rating = db.Column(db.Float, default=4.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cart_items = db.relationship('CartItem', backref='product', lazy='dynamic')
    wishlist_items = db.relationship('Wishlist', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    reviews = db.relationship('Review', backref='product', lazy='dynamic')

    @property
    def image_url(self):
        if self.image and not self.image.startswith('http'):
            return f'/static/images/{self.image}'
        return self.image or '/static/images/placeholder.jpg'

    def __repr__(self):
        return f'<Product {self.name}>'
