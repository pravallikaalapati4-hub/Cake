from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Category, Order, OrderItem, Review, ContactMessage
from utils.helpers import admin_required
from sqlalchemy import func
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        abort(403)


@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    revenue = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar()
    pending = Order.query.filter(Order.status.in_(['Pending', 'Confirmed', 'Preparing'])).count()
    completed = Order.query.filter_by(status='Delivered').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()

    # Simple chart data - last 7 days revenue
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        chart_labels.append(day.strftime('%a'))
        day_rev = db.session.query(func.coalesce(func.sum(Order.total_amount), 0)).filter(
            func.date(Order.created_at) == day
        ).scalar()
        chart_data.append(float(day_rev))

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_products=total_products,
                           total_orders=total_orders,
                           revenue=revenue,
                           pending=pending,
                           completed=completed,
                           recent_orders=recent_orders,
                           unread_messages=unread_messages,
                           chart_labels=chart_labels,
                           chart_data=chart_data)


@admin_bp.route('/products')
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)


@admin_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        ingredients = request.form.get('ingredients', '').strip()
        stock = request.form.get('stock', 50, type=int)
        rating = request.form.get('rating', 4.5, type=float)
        image = request.form.get('image', 'placeholder.jpg').strip()

        if not name or price is None or not category_id:
            flash('Name, price and category are required.', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=None)

        product = Product(
            name=name, description=description, price=price,
            category_id=category_id, ingredients=ingredients,
            stock=stock, rating=rating, image=image
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', categories=categories, product=None)


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name', product.name).strip()
        product.description = request.form.get('description', product.description)
        product.price = request.form.get('price', type=float) or product.price
        product.category_id = request.form.get('category_id', type=int) or product.category_id
        product.ingredients = request.form.get('ingredients', product.ingredients)
        product.stock = request.form.get('stock', type=int) if request.form.get('stock') else product.stock
        product.rating = request.form.get('rating', type=float) or product.rating
        product.image = request.form.get('image', product.image).strip()
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', categories=categories, product=product)


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/categories')
def categories():
    cats = Category.query.all()
    return render_template('admin/categories.html', categories=cats)


@admin_bp.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    if name:
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'danger')
        else:
            db.session.add(Category(name=name, description=description))
            db.session.commit()
            flash('Category added.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/edit/<int:cat_id>', methods=['POST'])
def edit_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    cat.name = request.form.get('name', cat.name).strip()
    cat.description = request.form.get('description', cat.description)
    db.session.commit()
    flash('Category updated.', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.products.count() > 0:
        flash('Cannot delete category with products.', 'danger')
    else:
        db.session.delete(cat)
        db.session.commit()
        flash('Category deleted.', 'info')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/orders')
def orders():
    status_filter = request.args.get('status', 'all')
    query = Order.query
    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)
    orders = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)


@admin_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    allowed = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
    if new_status in allowed:
        order.status = new_status
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))


@admin_bp.route('/users')
def users():
    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot deactivate admin.', 'danger')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'User {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/reviews')
def reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=reviews)


@admin_bp.route('/reviews/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'info')
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/messages')
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=messages)


@admin_bp.route('/messages/<int:msg_id>/read', methods=['POST'])
def mark_read(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    msg.is_read = True
    db.session.commit()
    return redirect(url_for('admin.messages'))


@admin_bp.route('/messages/delete/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message deleted.', 'info')
    return redirect(url_for('admin.messages'))
