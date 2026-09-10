import os
from flask import Flask
from config import Config
from extensions import db, login_manager
from utils.helpers import seed_database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from routes import auth_bp, main_bp, product_bp, cart_bp, order_bp, admin_bp, extra_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(extra_bp)

    @app.context_processor
    def inject_globals():
        from models import CartItem, Wishlist
        from flask_login import current_user
        cart_count = 0
        wishlist_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
            wishlist_count = Wishlist.query.filter_by(user_id=current_user.id).count()
        return dict(cart_count=cart_count, wishlist_count=wishlist_count)

    with app.app_context():
        db.create_all()
        seed_database()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
