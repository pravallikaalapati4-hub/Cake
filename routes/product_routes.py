from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from extensions import db
from models import Product, Category, Review, Wishlist
from sqlalchemy import or_

product_bp = Blueprint('product', __name__)


@product_bp.route('/menu')
def menu():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', 'all')
    sort = request.args.get('sort', 'featured')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = Product.query

    if q:
        query = query.filter(or_(
            Product.name.ilike(f'%{q}%'),
            Product.description.ilike(f'%{q}%')
        ))
    if category and category != 'all':
        cat = Category.query.filter_by(name=category).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'rating':
        query = query.order_by(Product.rating.desc())
    elif sort == 'newest':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.rating.desc())

    products = query.all()
    categories = Category.query.all()
    return render_template('menu.html',
                           products=products,
                           categories=categories,
                           current_category=category,
                           q=q,
                           sort=sort,
                           min_price=min_price,
                           max_price=max_price)


@product_bp.route('/product/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).limit(10).all()
    in_wishlist = False
    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first() is not None
    return render_template('product_details.html',
                           product=product,
                           related=related,
                           reviews=reviews,
                           in_wishlist=in_wishlist)


@product_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()
    if not rating or rating < 1 or rating > 5:
        flash('Please provide a valid rating (1-5).', 'danger')
        return redirect(url_for('product.product_details', product_id=product_id))
    existing = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if existing:
        existing.rating = rating
        existing.comment = comment
    else:
        review = Review(user_id=current_user.id, product_id=product_id, rating=rating, comment=comment)
        db.session.add(review)
    # Update average rating
    all_reviews = Review.query.filter_by(product_id=product_id).all()
    if all_reviews:
        product.rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 1)
    db.session.commit()
    flash('Thank you for your review!', 'success')
    return redirect(url_for('product.product_details', product_id=product_id))


@product_bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('account/wishlist.html', items=items)


@product_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'removed'})
        flash('Removed from wishlist.', 'info')
    else:
        db.session.add(Wishlist(user_id=current_user.id, product_id=product_id))
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'added'})
        flash('Added to wishlist!', 'success')
    return redirect(request.referrer or url_for('product.menu'))


@product_bp.route('/wishlist/remove/<int:product_id>', methods=['POST'])
@login_required
def remove_wishlist(product_id):
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Removed from wishlist.', 'info')
    return redirect(url_for('product.wishlist'))
