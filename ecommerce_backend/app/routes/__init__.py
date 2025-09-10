"""
Routes package for the ecommerce_backend.

Each module in this package registers a Flask-Smorest Blueprint:
- health.py: Health check
- auth.py: Authentication (signup/login/me)
- users.py: User profile/admin listing
- categories.py: Category CRUD
- products.py: Product CRUD
- cart.py: Shopping cart operations
- orders.py: Order placement and retrieval
- payments.py: Mock payment processing
"""
# Package marker. Blueprints are imported and registered in app.__init__.
