from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from ecommerce_database.models import User, UserRole, Cart
from ..schemas.auth import SignupSchema, LoginSchema, TokenSchema
from ..schemas.user import UserOutSchema
from ..utils.auth import hash_password, verify_password, create_tokens
from ..utils.common import error_response

blp = Blueprint("Auth", "auth", url_prefix="/auth", description="Authentication endpoints")


@blp.route("/signup")
class SignupView(MethodView):
    def post(self):
        """
        Create a new user account.

        Request: SignupSchema
        Response: { user: UserOutSchema, tokens: TokenSchema }
        """
        payload = SignupSchema().load(request.json or {})
        session = current_app.session

        user = User(
            email=payload["email"].lower(),
            password_hash=hash_password(payload["password"]),
            full_name=payload["full_name"],
            role=UserRole.CUSTOMER,
        )

        try:
            session.add(user)
            session.flush()

            # Create empty cart for user
            cart = Cart(user_id=user.id)
            session.add(cart)

            session.commit()
        except IntegrityError:
            session.rollback()
            return error_response("Email already registered.", 400)

        tokens = create_tokens(identity={"id": user.id, "email": user.email, "role": user.role.value})
        return {
            "user": UserOutSchema().dump(user),
            "tokens": TokenSchema().dump({"access_token": tokens.access_token, "refresh_token": tokens.refresh_token}),
        }, 201


@blp.route("/login")
class LoginView(MethodView):
    def post(self):
        """
        Login with credentials.

        Request: LoginSchema
        Response: TokenSchema + user info
        """
        payload = LoginSchema().load(request.json or {})
        session = current_app.session

        user = session.query(User).filter(User.email == payload["email"].lower()).one_or_none()
        if not user or not verify_password(payload["password"], user.password_hash):
            return error_response("Invalid email or password.", 401)

        tokens = create_tokens(identity={"id": user.id, "email": user.email, "role": user.role.value})
        return {
            "user": UserOutSchema().dump(user),
            "tokens": TokenSchema().dump({"access_token": tokens.access_token, "refresh_token": tokens.refresh_token}),
        }, 200


@blp.route("/me")
class MeView(MethodView):
    @jwt_required()
    def get(self):
        """Return current authenticated user's profile."""
        identity = get_jwt_identity()
        session = current_app.session
        user = session.query(User).get(identity["id"])
        if not user:
            return error_response("User not found.", 404)
        return UserOutSchema().dump(user), 200
