from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from extensions import db
from models import Product, Category, ContactMessage, Review, Order
from utils.helpers import get_recommendations

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    featured = Product.query.order_by(Product.rating.desc()).limit(6).all()
    bestsellers = Product.query.order_by(Product.rating.desc()).limit(4).all()
    categories = Category.query.all()
    combos = Product.query.filter(Product.category.has(name='Combos')).limit(3).all()
    recommendations = get_recommendations(current_user, limit=4) if current_user.is_authenticated else []
    return render_template('home.html',
                           featured=featured,
                           bestsellers=bestsellers,
                           categories=categories,
                           combos=combos,
                           recommendations=recommendations)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/offers')
def offers():
    combos = Product.query.filter(Product.category.has(name='Combos')).all()
    return render_template('offers.html', combos=combos)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if name and email and subject and message:
            msg = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(msg)
            db.session.commit()
            flash('Thank you! Your message has been sent. We will get back to you soon.', 'success')
            return redirect(url_for('main.contact'))
        flash('Please fill in all fields.', 'danger')
    return render_template('contact.html')


@main_bp.route('/faq')
def faq():
    return render_template('faq.html')


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.address = request.form.get('address', current_user.address)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('main.profile'))
    return render_template('account/profile.html')


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
