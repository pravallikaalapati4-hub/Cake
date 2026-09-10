from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Product, Poll, PollVote, CustomOrder, Category
from utils.helpers import get_recommendations
from sqlalchemy import func, case

extra_bp = Blueprint('extra', __name__)


@extra_bp.route('/recommendations')
@login_required
def recommendations():
    recs = get_recommendations(current_user, limit=8)
    return render_template('extra/recommendations.html', products=recs)


@extra_bp.route('/poll', methods=['GET', 'POST'])
@login_required
def poll():
    poll = Poll.query.filter_by(is_active=True).first()
    if not poll:
        flash('No active poll at the moment.', 'info')
        return redirect(url_for('main.home'))

    products = Product.query.order_by(Product.name).all()
    existing = PollVote.query.filter_by(poll_id=poll.id, user_id=current_user.id).all()
    user_votes = {v.rank: v.product_id for v in existing}

    if request.method == 'POST':
        rank1 = request.form.get('rank1', type=int)
        rank2 = request.form.get('rank2', type=int)
        rank3 = request.form.get('rank3', type=int)

        selected = [rank1, rank2, rank3]
        if not all(selected) or len(set(selected)) < 3:
            flash('Please select 3 different products for 1st, 2nd and 3rd place.', 'danger')
            return render_template('extra/poll.html', poll=poll, products=products, user_votes=user_votes)

        # Remove old votes
        PollVote.query.filter_by(poll_id=poll.id, user_id=current_user.id).delete()
        for rank, pid in enumerate(selected, start=1):
            db.session.add(PollVote(
                poll_id=poll.id,
                user_id=current_user.id,
                product_id=pid,
                rank=rank
            ))
        db.session.commit()
        flash('Thanks for voting! Your top 3 favourites have been saved.', 'success')
        return redirect(url_for('extra.poll_results'))

    return render_template('extra/poll.html', poll=poll, products=products, user_votes=user_votes)


@extra_bp.route('/poll/results')
def poll_results():
    poll = Poll.query.filter_by(is_active=True).first()
    if not poll:
        flash('No active poll.', 'info')
        return redirect(url_for('main.home'))

    # Weighted score: rank1=3pts, rank2=2pts, rank3=1pt
    votes = db.session.query(
        PollVote.product_id,
        func.sum(
            case(
                (PollVote.rank == 1, 3),
                (PollVote.rank == 2, 2),
                (PollVote.rank == 3, 1),
                else_=0
            )
        ).label('score'),
        func.count(PollVote.id).label('vote_count')
    ).filter_by(poll_id=poll.id).group_by(PollVote.product_id).order_by(
        db.desc('score')
    ).all()

    results = []
    for product_id, score, vote_count in votes:
        product = Product.query.get(product_id)
        if product:
            results.append({
                'product': product,
                'score': int(score or 0),
                'vote_count': vote_count
            })

    total_voters = db.session.query(func.count(func.distinct(PollVote.user_id))).filter_by(poll_id=poll.id).scalar() or 0
    return render_template('extra/poll_results.html', poll=poll, results=results, total_voters=total_voters)


@extra_bp.route('/custom-order', methods=['GET', 'POST'])
@login_required
def custom_order():
    products = Product.query.filter(
        Product.category.has(Category.name.in_(['Cakes', 'Cupcakes', 'Combos']))
    ).all()

    if request.method == 'POST':
        base_id = request.form.get('base_product_id', type=int) or None
        cake_message = request.form.get('cake_message', '').strip()[:100]
        size = request.form.get('size', 'Regular')
        flavour_notes = request.form.get('flavour_notes', '').strip()[:200]
        special = request.form.get('special_instructions', '').strip()
        delivery_date = request.form.get('delivery_date', '').strip()

        if not flavour_notes and not cake_message and not special:
            flash('Please add at least a message, flavour note or special instruction.', 'danger')
            return render_template('extra/custom_order.html', products=products)

        # Simple price estimate
        base_price = 499
        if base_id:
            p = Product.query.get(base_id)
            if p:
                base_price = p.price
        size_extra = {'Regular': 0, 'Medium': 150, 'Large': 300}.get(size, 0)
        estimated = base_price + size_extra + (50 if cake_message else 0)

        co = CustomOrder(
            user_id=current_user.id,
            base_product_id=base_id,
            cake_message=cake_message or None,
            size=size,
            flavour_notes=flavour_notes or None,
            special_instructions=special or None,
            delivery_date=delivery_date or None,
            estimated_price=estimated,
            status='Pending'
        )
        db.session.add(co)
        db.session.commit()
        flash(f'Custom order submitted! Estimated price ₹{estimated:.0f}. We will confirm soon.', 'success')
        return redirect(url_for('extra.my_custom_orders'))

    return render_template('extra/custom_order.html', products=products)


@extra_bp.route('/my-custom-orders')
@login_required
def my_custom_orders():
    orders = CustomOrder.query.filter_by(user_id=current_user.id).order_by(CustomOrder.created_at.desc()).all()
    return render_template('extra/my_custom_orders.html', orders=orders)
