from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import CartItem, Product
from config import Config

cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/cart')
@login_required
def view_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = sum(item.subtotal() for item in items)
    delivery = 0 if subtotal >= Config.FREE_DELIVERY_THRESHOLD else (Config.DELIVERY_FEE if items else 0)
    total = subtotal + delivery
    return render_template('cart/cart.html',
                           items=items,
                           subtotal=subtotal,
                           delivery=delivery,
                           total=total,
                           free_threshold=Config.FREE_DELIVERY_THRESHOLD)


@cart_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = request.form.get('quantity', 1, type=int)
    if qty < 1:
        qty = 1
    if product.stock < qty:
        flash('Not enough stock available.', 'danger')
        return redirect(request.referrer or url_for('product.menu'))

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += qty
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=qty)
        db.session.add(item)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'status': 'ok', 'cart_count': count, 'message': f'{product.name} added to cart'})
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))


@cart_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('cart.view_cart'))
    qty = request.form.get('quantity', type=int)
    if qty is None or qty < 1:
        db.session.delete(item)
    else:
        if qty > item.product.stock:
            flash('Not enough stock.', 'danger')
            return redirect(url_for('cart.view_cart'))
        item.quantity = qty
    db.session.commit()
    flash('Cart updated.', 'success')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('cart.view_cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/cart/count')
@login_required
def cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})
