from decimal import Decimal
from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ecommerce_database.models import Cart, CartItem, Product
from ..schemas.cart import CartItemInSchema, CartOutSchema
from ..utils.common import error_response

blp = Blueprint("Cart", "cart", url_prefix="/cart", description="Shopping cart operations")


def _get_or_create_cart(session, user_id: int) -> Cart:
    cart = session.query(Cart).filter(Cart.user_id == user_id).one_or_none()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.flush()
    return cart


@blp.route("")
class CartView(MethodView):
    @jwt_required()
    def get(self):
        """Get current user's cart."""
        identity = get_jwt_identity()
        session = current_app.session
        cart = _get_or_create_cart(session, identity["id"])
        return CartOutSchema().dump(cart), 200

    @jwt_required()
    def delete(self):
        """Clear current user's cart."""
        identity = get_jwt_identity()
        session = current_app.session
        cart = _get_or_create_cart(session, identity["id"])
        cart.items.clear()
        session.commit()
        return {"message": "Cart cleared"}, 200


@blp.route("/items")
class CartItemsView(MethodView):
    @jwt_required()
    def post(self):
        """Add or update an item in the cart."""
        identity = get_jwt_identity()
        payload = CartItemInSchema().load(request.json or {})
        session = current_app.session
        cart = _get_or_create_cart(session, identity["id"])
        product = session.query(Product).get(payload["product_id"])
        if not product:
            return error_response("Product not found.", 404)

        # find existing
        item = None
        for it in cart.items:
            if it.product_id == product.id:
                item = it
                break

        if item:
            item.quantity = payload["quantity"]
        else:
            unit_price = Decimal(str(product.price))
            item = CartItem(cart_id=cart.id, product_id=product.id, quantity=payload["quantity"], unit_price=unit_price)
            session.add(item)
        session.commit()
        session.refresh(cart)
        return CartOutSchema().dump(cart), 200

    @jwt_required()
    def delete(self):
        """Remove an item from the cart (by product_id in body)."""
        identity = get_jwt_identity()
        session = current_app.session
        product_id = (request.json or {}).get("product_id")
        if not product_id:
            return error_response("product_id required", 400)
        cart = _get_or_create_cart(session, identity["id"])
        to_remove = [it for it in cart.items if it.product_id == int(product_id)]
        if not to_remove:
            return error_response("Item not found in cart.", 404)
        for it in to_remove:
            session.delete(it)
        session.commit()
        session.refresh(cart)
        return CartOutSchema().dump(cart), 200
