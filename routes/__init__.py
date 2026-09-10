from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.admin_routes import admin_bp
from routes.extra_routes import extra_bp

__all__ = ['auth_bp', 'main_bp', 'product_bp', 'cart_bp', 'order_bp', 'admin_bp', 'extra_bp']
