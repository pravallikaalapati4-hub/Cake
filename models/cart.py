from extensions import db


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    def subtotal(self):
        return self.quantity * self.product.price

    def __repr__(self):
        return f'<CartItem user={self.user_id} product={self.product_id}>'


class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist'),)

    def __repr__(self):
        return f'<Wishlist user={self.user_id} product={self.product_id}>'
