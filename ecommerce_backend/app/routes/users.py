from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ecommerce_database.models import User, UserRole
from ..schemas.user import UserOutSchema, UserUpdateSchema
from ..utils.auth import hash_password
from ..utils.common import error_response, get_pagination_params

blp = Blueprint("Users", "users", url_prefix="/users", description="User account management")


@blp.route("/me")
class UserMeView(MethodView):
    @jwt_required()
    def get(self):
        """Get current user's profile."""
        identity = get_jwt_identity()
        session = current_app.session
        user = session.query(User).get(identity["id"])
        if not user:
            return error_response("User not found.", 404)
        return UserOutSchema().dump(user), 200

    @jwt_required()
    def put(self):
        """Update current user's profile (full_name, password)."""
        identity = get_jwt_identity()
        session = current_app.session
        user = session.query(User).get(identity["id"])
        if not user:
            return error_response("User not found.", 404)

        data = UserUpdateSchema().load(request.json or {})
        if "full_name" in data and data["full_name"]:
            user.full_name = data["full_name"]
        if "password" in data and data["password"]:
            user.password_hash = hash_password(data["password"])
        session.commit()
        return UserOutSchema().dump(user), 200


@blp.route("")
class UsersAdminView(MethodView):
    @jwt_required()
    def get(self):
        """Admin: list users with pagination."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)

        session = current_app.session
        page, page_size = get_pagination_params()
        q = session.query(User)
        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()
        return {
            "data": UserOutSchema(many=True).dump(items),
            "meta": {"total": total, "page": page, "page_size": page_size},
        }, 200
