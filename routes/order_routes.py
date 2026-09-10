from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import CartItem, Order, OrderItem, Product
from config import Config
from datetime import datetime, timedelta

order_bp = Blueprint('order', __name__)


@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('cart.view_cart'))

    subtotal = sum(item.subtotal() for item in items)
    delivery = 0 if subtotal >= Config.FREE_DELIVERY_THRESHOLD else Config.DELIVERY_FEE
    total = subtotal + delivery

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        payment = request.form.get('payment_method', 'Cash on Delivery')

        if not all([full_name, phone, address, city, state, pincode]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('cart/checkout.html',
                                   items=items, subtotal=subtotal,
                                   delivery=delivery, total=total)

        delivery_address = f"{full_name}\n{address}\n{city}, {state} - {pincode}\nPhone: {phone}"
        if email:
            delivery_address += f"\nEmail: {email}"

        # Stock check
        for item in items:
            if item.product.stock < item.quantity:
                flash(f'Insufficient stock for {item.product.name}.', 'danger')
                return redirect(url_for('cart.view_cart'))

        order = Order(
            user_id=current_user.id,
            total_amount=total,
            delivery_address=delivery_address,
            payment_method=payment,
            status='Pending'
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            db.session.add(oi)
            item.product.stock -= item.quantity
            db.session.delete(item)

        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order.confirmation', order_id=order.id))

    return render_template('cart/checkout.html',
                           items=items, subtotal=subtotal,
                           delivery=delivery, total=total)


@order_bp.route('/order/confirmation/<int:order_id>')
@login_required
def confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.home'))
    est_delivery = order.created_at + timedelta(hours=90)  # ~3-4 days feel
    return render_template('orders/confirmation.html', order=order, est_delivery=est_delivery)


@order_bp.route('/orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/my_orders.html', orders=orders)


@order_bp.route('/order/<int:order_id>')
@login_required
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('order.my_orders'))
    return render_template('orders/order_details.html', order=order)


@order_bp.route('/order/track/<int:order_id>')
@login_required
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('order.my_orders'))
    return render_template('orders/track.html', order=order)
