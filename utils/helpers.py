from functools import wraps
from collections import Counter
from flask import abort
from flask_login import current_user
from extensions import db
from models import Category, Product, User, Order, OrderItem, Wishlist, Poll, PollVote


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Reliable dessert image URLs (Unsplash)
PRODUCT_IMAGES = {
    'Classic Coke Cupcake': 'https://images.unsplash.com/photo-1614707267537-b85aaf00c4b7?w=600&h=600&fit=crop',
    'Coca-Cola Chocolate Cupcake': 'https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=600&h=600&fit=crop',
    'Cherry Coke Cream Cupcake': 'https://images.unsplash.com/photo-1587668178277-295251f900ce?w=600&h=600&fit=crop',
    'Classic Coke Celebration Cake': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&h=600&fit=crop',
    'Coke Chocolate Fudge Cake': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?w=600&h=600&fit=crop',
    'Coke Red Velvet Cake': 'https://images.unsplash.com/photo-1616541823729-00fe0aacd32c?w=600&h=600&fit=crop',
    'Coke Caramel Pastry': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&h=600&fit=crop',
    'Chocolate Coke Pastry': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=600&h=600&fit=crop',
    'Coke Cream Puff': 'https://images.unsplash.com/photo-1612203985729-70726943d5c0?w=600&h=600&fit=crop',
    'Coke Cream Jar': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600&h=600&fit=crop',
    'Fizz & Cream Cup': 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=600&h=600&fit=crop',
    'Coke Chocolate Mousse': 'https://images.unsplash.com/photo-1541783245831-57d6fb0926d3?w=600&h=600&fit=crop',
    'Coke Bake Mini Box': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=600&h=600&fit=crop',
    'Party Dessert Box': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=600&h=600&fit=crop',
    'Ultimate Coke Dessert Combo': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=600&h=600&fit=crop',
}


def get_recommendations(user, limit=6):
    """Personalized recommendations based on order history, wishlist, and popular items."""
    if not user or not user.is_authenticated:
        return Product.query.order_by(Product.rating.desc()).limit(limit).all()

    preferred_cat_ids = []
    liked_product_ids = set()

    # From past orders
    orders = Order.query.filter_by(user_id=user.id).all()
    for order in orders:
        for item in order.items:
            liked_product_ids.add(item.product_id)
            if item.product:
                preferred_cat_ids.append(item.product.category_id)

    # From wishlist
    for w in Wishlist.query.filter_by(user_id=user.id).all():
        liked_product_ids.add(w.product_id)
        if w.product:
            preferred_cat_ids.append(w.product.category_id)

    recommended = []
    seen = set(liked_product_ids)

    if preferred_cat_ids:
        top_cats = [c for c, _ in Counter(preferred_cat_ids).most_common(3)]
        for cat_id in top_cats:
            for p in Product.query.filter_by(category_id=cat_id).order_by(Product.rating.desc()).limit(4).all():
                if p.id not in seen:
                    recommended.append(p)
                    seen.add(p.id)
                if len(recommended) >= limit:
                    return recommended[:limit]

    # Fill with top-rated
    for p in Product.query.order_by(Product.rating.desc()).all():
        if p.id not in seen:
            recommended.append(p)
            seen.add(p.id)
        if len(recommended) >= limit:
            break

    return recommended[:limit]


def seed_database():
    """Populate initial categories, products, poll and admin user if empty."""
    if not Category.query.first():
        categories_data = [
            ('Cupcakes', 'Delightful Coca-Cola inspired cupcakes'),
            ('Cakes', 'Celebration cakes with a fizzy twist'),
            ('Pastries', 'Flaky and creamy Coca-Cola pastries'),
            ('Cream Desserts', 'Smooth cream-filled desserts'),
            ('Combos', 'Special dessert boxes and combos'),
        ]
        for name, desc in categories_data:
            db.session.add(Category(name=name, description=desc))
        db.session.commit()

        cats = {c.name: c.id for c in Category.query.all()}

        products = [
            ('Classic Coke Cupcake', 'Soft vanilla cupcake infused with Coca-Cola syrup, topped with creamy frosting.', 149, cats['Cupcakes'], 'Flour, sugar, Coca-Cola syrup, butter, eggs, vanilla', 80, 4.8),
            ('Coca-Cola Chocolate Cupcake', 'Rich chocolate cupcake with a cola caramel center.', 169, cats['Cupcakes'], 'Cocoa, flour, Coca-Cola, dark chocolate, cream', 70, 4.9),
            ('Cherry Coke Cream Cupcake', 'Cherry-cola flavoured cupcake with whipped cream topping.', 159, cats['Cupcakes'], 'Flour, cherry extract, Coca-Cola, cream cheese frosting', 65, 4.7),
            ('Classic Coke Celebration Cake', 'Layered sponge cake soaked in cola syrup with buttercream.', 899, cats['Cakes'], 'Flour, eggs, Coca-Cola, buttercream, fondant', 25, 4.9),
            ('Coke Chocolate Fudge Cake', 'Decadent chocolate fudge cake with cola ganache.', 999, cats['Cakes'], 'Dark chocolate, Coca-Cola, cream, cocoa powder', 20, 4.8),
            ('Coke Red Velvet Cake', 'Red velvet layers with a subtle cola note and cream cheese frosting.', 1099, cats['Cakes'], 'Cocoa, buttermilk, Coca-Cola, cream cheese', 18, 4.9),
            ('Coke Caramel Pastry', 'Puff pastry filled with cola-caramel cream.', 129, cats['Pastries'], 'Puff pastry, caramel, Coca-Cola, cream', 60, 4.6),
            ('Chocolate Coke Pastry', 'Chocolate pastry with cola mousse filling.', 139, cats['Pastries'], 'Chocolate, puff pastry, Coca-Cola mousse', 55, 4.7),
            ('Coke Cream Puff', 'Light choux pastry filled with cola whipped cream.', 119, cats['Pastries'], 'Choux pastry, Coca-Cola cream, sugar', 70, 4.5),
            ('Coke Cream Jar', 'Layered cream dessert in a jar with cola jelly.', 199, cats['Cream Desserts'], 'Cream, Coca-Cola jelly, biscuit crumbs', 40, 4.8),
            ('Fizz & Cream Cup', 'Sparkling cola jelly topped with vanilla cream.', 179, cats['Cream Desserts'], 'Cola jelly, whipped cream, mint', 45, 4.7),
            ('Coke Chocolate Mousse', 'Silky chocolate mousse with a cola twist.', 189, cats['Cream Desserts'], 'Dark chocolate, cream, Coca-Cola reduction', 35, 4.9),
            ('Coke Bake Mini Box', 'Assorted mini cupcakes and pastries – perfect for two.', 499, cats['Combos'], 'Assorted mini desserts', 30, 4.8),
            ('Party Dessert Box', 'A shareable box of cakes, cupcakes and cream desserts.', 1299, cats['Combos'], 'Selection of bestsellers', 20, 4.9),
            ('Ultimate Coke Dessert Combo', 'The complete Coca-Cola dessert experience for the family.', 1899, cats['Combos'], 'Full range of signature desserts', 15, 5.0),
        ]

        for name, desc, price, cat_id, ingredients, stock, rating in products:
            img = PRODUCT_IMAGES.get(name, '')
            db.session.add(Product(
                name=name,
                description=desc,
                price=price,
                image=img,
                category_id=cat_id,
                ingredients=ingredients,
                stock=stock,
                rating=rating
            ))
        db.session.commit()

    # Always refresh images to Unsplash URLs if missing
    for p in Product.query.all():
        if p.name in PRODUCT_IMAGES and (not p.image or not p.image.startswith('http')):
            p.image = PRODUCT_IMAGES[p.name]
    db.session.commit()

    # Default admin
    if not User.query.filter_by(email='admin@cokebake.com').first():
        admin = User(
            name='Admin',
            email='admin@cokebake.com',
            phone='9999999999',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    # Demo customer
    if not User.query.filter_by(email='customer@cokebake.com').first():
        customer = User(
            name='Demo Customer',
            email='customer@cokebake.com',
            phone='9876543210',
            address='123 Sweet Street, Mumbai, Maharashtra 400001',
            is_admin=False,
            is_active=True
        )
        customer.set_password('customer123')
        db.session.add(customer)
        db.session.commit()

    # Active poll
    if not Poll.query.filter_by(is_active=True).first():
        poll = Poll(
            title='Vote for Your Top 3 Favourite Desserts!',
            description='Pick your 3 favourite Coke Bake desserts. Rank them 1st, 2nd and 3rd. Help us decide what to feature next!',
            is_active=True
        )
        db.session.add(poll)
        db.session.commit()
