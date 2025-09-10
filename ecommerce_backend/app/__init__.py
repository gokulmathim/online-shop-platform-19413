from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from .config import Config
from .routes.health import blp as health_blp

# Import blueprints
from .routes.auth import blp as auth_blp
from .routes.users import blp as users_blp
from .routes.categories import blp as categories_blp
from .routes.products import blp as products_blp
from .routes.cart import blp as cart_blp
from .routes.orders import blp as orders_blp
from .routes.payments import blp as payments_blp

# Database session utilities from ecommerce_database
from ecommerce_database.db.session import get_session

app = Flask(__name__)
app.url_map.strict_slashes = False

# Load config
app.config.from_object(Config)

# CORS
CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

# OpenAPI / Swagger UI (flask-smorest)
app.config["API_TITLE"] = app.config.get("API_TITLE", "E-commerce Backend API")
app.config["API_VERSION"] = app.config.get("API_VERSION", "v1")
app.config["OPENAPI_VERSION"] = app.config.get("OPENAPI_VERSION", "3.0.3")
app.config["OPENAPI_URL_PREFIX"] = app.config.get("OPENAPI_URL_PREFIX", "/docs")
app.config["OPENAPI_SWAGGER_UI_PATH"] = app.config.get("OPENAPI_SWAGGER_UI_PATH", "")
app.config["OPENAPI_SWAGGER_UI_URL"] = app.config.get("OPENAPI_SWAGGER_UI_URL")

api = Api(app)

# Provide global tags for better grouping in OpenAPI UI
api.spec.components.security_scheme(
    "BearerAuth",
    {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
)
api.spec.options["tags"] = [
    {"name": "Health", "description": "Health check route"},
    {"name": "Auth", "description": "Authentication endpoints (signup, login, logout, refresh)"},
    {"name": "Users", "description": "User account management"},
    {"name": "Categories", "description": "Product categories management"},
    {"name": "Products", "description": "Product CRUD"},
    {"name": "Cart", "description": "Shopping cart operations"},
    {"name": "Orders", "description": "Order placement and history"},
    {"name": "Payments", "description": "Payment processing (mock)"},
]

# JWT
jwt = JWTManager(app)

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"message": "Invalid token", "reason": reason}), 401

@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify({"message": "Missing authorization", "reason": reason}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "Token expired"}), 401

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(users_blp)
api.register_blueprint(categories_blp)
api.register_blueprint(products_blp)
api.register_blueprint(cart_blp)
api.register_blueprint(orders_blp)
api.register_blueprint(payments_blp)

# Session management: provide and remove DB session per request (simple pattern)
@app.before_request
def _create_session():
    # attach to flask global via app context
    app.session = get_session()

@app.teardown_request
def _remove_session(exc):
    # Ensure the session is closed and removed even in exception cases
    sess = getattr(app, "session", None)
    if sess is not None:
        try:
            if exc:
                sess.rollback()
        finally:
            sess.close()
            app.session = None
