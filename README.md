<<<<<<< HEAD
# Cake
=======
# Coke Bake

**Taste the Fizz. Love the Bake.**

A complete, premium full-stack dessert e-commerce website inspired by Coca-Cola flavours. Built with Flask, SQLAlchemy, Flask-Login, and a modern responsive UI.

## Features

### Customer
- Stunning home page with hero, featured products, categories, reviews & CTA
- Full menu with search, category filters, price filters & sorting
- Product detail pages with reviews, wishlist & related items
- User registration / login with secure password hashing
- Shopping cart with quantity updates
- Checkout (Cash on Delivery, UPI & Card UI simulation)
- Order confirmation, history & timeline tracking
- Wishlist, profile management
- Offers, About, Contact (messages stored in DB), FAQ

### Admin Dashboard
- Statistics: users, products, orders, revenue, pending/completed
- Chart.js revenue chart (last 7 days)
- Product CRUD (add / edit / delete / stock / price)
- Category management
- Order management with status updates
- User activate / deactivate
- Review moderation
- Contact message inbox

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python, Flask           |
| Database   | SQLite + SQLAlchemy ORM |
| Auth       | Flask-Login, Werkzeug   |
| Frontend   | HTML5, CSS3, Vanilla JS |
| Charts     | Chart.js (CDN)          |

## Installation

```bash
# Clone / enter project
cd coke_bake

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS / Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Open **http://127.0.0.1:5000**

The database is created and seeded automatically on first run.

## Demo Accounts

| Role     | Email                 | Password    |
|----------|-----------------------|-------------|
| Admin    | admin@cokebake.com    | admin123    |
| Customer | customer@cokebake.com | customer123 |

## Project Structure

```
coke_bake/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── README.md
├── database/
│   └── coke_bake.db          # auto-created
├── models/
│   ├── user.py, product.py, category.py
│   ├── cart.py, order.py, review.py
├── routes/
│   ├── auth_routes.py, main_routes.py
│   ├── product_routes.py, cart_routes.py
│   ├── order_routes.py, admin_routes.py
├── templates/
│   ├── base.html, home.html, menu.html, ...
│   ├── auth/, cart/, orders/, account/, admin/, errors/
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── utils/
    └── helpers.py
```

## Sample Products

Cupcakes, Cakes, Pastries, Cream Desserts and Combos are pre-seeded with realistic Indian Rupee pricing.

## Notes

- Images use elegant emoji placeholders for a polished look without external dependencies.
- Payment gateways are UI-only simulations (no real charges).
- All routes, cart, checkout, admin CRUD and authentication are fully functional.
- Fully responsive (desktop, tablet, mobile) with hamburger navigation.

© 2026 Coke Bake. All Rights Reserved.
>>>>>>> 9de0348 (initial commit)
