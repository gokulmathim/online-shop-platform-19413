from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from ecommerce_database.models import Category, UserRole
from ..schemas.category import CategoryInSchema, CategoryOutSchema
from ..utils.common import error_response, get_pagination_params

blp = Blueprint("Categories", "categories", url_prefix="/categories", description="Product categories management")


@blp.route("")
class CategoryListView(MethodView):
    def get(self):
        """List categories with pagination."""
        session = current_app.session
        page, page_size = get_pagination_params()
        q = session.query(Category)
        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()
        return {"data": CategoryOutSchema(many=True).dump(items), "meta": {"total": total, "page": page, "page_size": page_size}}, 200

    @jwt_required()
    def post(self):
        """Admin: create category."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)

        payload = CategoryInSchema().load(request.json or {})
        session = current_app.session
        cat = Category(name=payload["name"], description=payload.get("description"))
        try:
            session.add(cat)
            session.commit()
        except IntegrityError:
            session.rollback()
            return error_response("Category already exists.", 400)
        return CategoryOutSchema().dump(cat), 201


@blp.route("/<int:category_id>")
class CategoryDetailView(MethodView):
    def get(self, category_id: int):
        """Get category by ID."""
        session = current_app.session
        cat = session.query(Category).get(category_id)
        if not cat:
            return error_response("Category not found.", 404)
        return CategoryOutSchema().dump(cat), 200

    @jwt_required()
    def put(self, category_id: int):
        """Admin: update category."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)
        session = current_app.session
        cat = session.query(Category).get(category_id)
        if not cat:
            return error_response("Category not found.", 404)
        data = CategoryInSchema().load(request.json or {})
        cat.name = data["name"]
        cat.description = data.get("description")
        session.commit()
        return CategoryOutSchema().dump(cat), 200

    @jwt_required()
    def delete(self, category_id: int):
        """Admin: delete category."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)
        session = current_app.session
        cat = session.query(Category).get(category_id)
        if not cat:
            return error_response("Category not found.", 404)
        session.delete(cat)
        session.commit()
        return {"message": "Deleted"}, 200
