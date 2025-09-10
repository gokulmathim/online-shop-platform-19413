from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from ecommerce_database.models import Product, ProductImage, ProductInventory, UserRole
from ..schemas.product import ProductInSchema, ProductOutSchema
from ..utils.common import error_response, get_pagination_params

blp = Blueprint("Products", "products", url_prefix="/products", description="Product CRUD")


@blp.route("")
class ProductListView(MethodView):
    def get(self):
        """List products with pagination (optionally filter by category_id, q)."""
        session = current_app.session
        page, page_size = get_pagination_params()
        q = session.query(Product)
        # Simple filters
        category_id = request.args.get("category_id")
        search = request.args.get("q")
        if category_id:
            try:
                cid = int(category_id)
                q = q.filter(Product.category_id == cid)
            except ValueError:
                pass
        if search:
            from sqlalchemy import or_
            like = f"%{search}%"
            q = q.filter(or_(Product.name.ilike(like)))
        total = q.count()
        items = q.offset((page - 1) * page_size).limit(page_size).all()
        return {"data": ProductOutSchema(many=True).dump(items), "meta": {"total": total, "page": page, "page_size": page_size}}, 200

    @jwt_required()
    def post(self):
        """Admin: create product with optional images and inventory."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)

        data = ProductInSchema().load(request.json or {})
        session = current_app.session
        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            category_id=data.get("category_id"),
        )
        try:
            session.add(product)
            session.flush()
            # images
            for img in data.get("images") or []:
                session.add(ProductImage(product_id=product.id, url=img["url"], alt_text=img.get("alt_text")))
            # inventory
            inv = data.get("inventory")
            if inv:
                session.add(ProductInventory(product_id=product.id, quantity=inv["quantity"]))
            session.commit()
        except IntegrityError:
            session.rollback()
            return error_response("Failed to create product.", 400)
        session.refresh(product)
        return ProductOutSchema().dump(product), 201


@blp.route("/<int:product_id>")
class ProductDetailView(MethodView):
    def get(self, product_id: int):
        """Get product by ID."""
        session = current_app.session
        product = session.query(Product).get(product_id)
        if not product:
            return error_response("Product not found.", 404)
        return ProductOutSchema().dump(product), 200

    @jwt_required()
    def put(self, product_id: int):
        """Admin: update product (basic fields)."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)
        session = current_app.session
        product = session.query(Product).get(product_id)
        if not product:
            return error_response("Product not found.", 404)
        data = ProductInSchema(partial=True).load(request.json or {})
        if "name" in data:
            product.name = data["name"]
        if "description" in data:
            product.description = data.get("description")
        if "price" in data:
            product.price = data["price"]
        if "category_id" in data:
            product.category_id = data.get("category_id")
        session.commit()
        return ProductOutSchema().dump(product), 200

    @jwt_required()
    def delete(self, product_id: int):
        """Admin: delete product."""
        identity = get_jwt_identity()
        if identity.get("role") != UserRole.ADMIN.value:
            return error_response("Forbidden", 403)
        session = current_app.session
        product = session.query(Product).get(product_id)
        if not product:
            return error_response("Product not found.", 404)
        session.delete(product)
        session.commit()
        return {"message": "Deleted"}, 200
