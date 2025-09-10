from decimal import Decimal
from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from ecommerce_database.models import (
    Order, OrderItem, OrderStatus, Product, ProductInventory, Cart
)
from ..schemas.order import OrderCreateSchema, OrderOutSchema
from ..utils.common import error_response, get_pagination_params

blp = Blueprint("Orders", "orders", url_prefix="/orders", description="Order placement and history")


def _calculate_totals(session, items_payload):
    subtotal = Decimal("0.00")
    items_detail = []
    for it in items_payload:
        product = session.query(Product).get(it["product_id"])
        if not product:
            raise ValueError(f"Product {it['product_id']} not found")
        qty = int(it["quantity"])
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        unit_price = Decimal(str(product.price))
        line_total = unit_price * qty
        items_detail.append((product, qty, unit_price, line_total))
        subtotal += line_total
    # Simplified shipping/tax
    shipping = Decimal("9.99") if subtotal > 0 else Decimal("0.00")
    tax = (subtotal * Decimal("0.07")).quantize(Decimal("0.01"))
    total = subtotal + shipping + tax
    return items_detail, subtotal, shipping, tax, total


@blp.route("")
class OrdersListView(MethodView):
    @jwt_required()
    def get(self):
        """List current user's orders."""
        identity = get_jwt_identity()
        session = current_app.session
        page, page_size = get_pagination_params()
        q = session.query(Order).filter(Order.user_id == identity["id"]).order_by(Order.created_at.desc())
        total = q.count()
        orders = q.offset((page - 1) * page_size).limit(page_size).all()
        return {"data": OrderOutSchema(many=True).dump(orders), "meta": {"total": total, "page": page, "page_size": page_size}}, 200

    @jwt_required()
    def post(self):
        """Create an order from provided items or from cart if no items provided."""
        identity = get_jwt_identity()
        payload = OrderCreateSchema().load(request.json or {})
        session = current_app.session

        items_payload = payload.get("items")
        if not items_payload:
            # build from cart
            cart = session.query(Cart).filter(Cart.user_id == identity["id"]).one_or_none()
            if not cart or not cart.items:
                return error_response("Cart is empty.", 400)
            items_payload = [{"product_id": it.product_id, "quantity": it.quantity} for it in cart.items]

        try:
            details, subtotal, shipping, tax, total = _calculate_totals(session, items_payload)

            order = Order(
                user_id=identity["id"],
                shipping_address_id=payload.get("shipping_address_id"),
                billing_address_id=payload.get("billing_address_id"),
                status=OrderStatus.PENDING,
                subtotal_amount=subtotal,
                shipping_amount=shipping,
                tax_amount=tax,
                total_amount=total,
            )
            session.add(order)
            session.flush()

            for product, qty, unit_price, line_total in details:
                session.add(OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=unit_price,
                    quantity=qty,
                    line_total=line_total
                ))
                # decrease inventory if available record exists
                if product.inventory:
                    inv: ProductInventory = product.inventory
                    inv.quantity = max(0, int(inv.quantity) - qty)

            # clear cart if generated from cart
            if not request.json or not request.json.get("items"):
                cart = session.query(Cart).filter(Cart.user_id == identity["id"]).one_or_none()
                if cart:
                    cart.items.clear()

            session.commit()
        except (ValueError, SQLAlchemyError) as e:
            session.rollback()
            return error_response(f"Failed to create order: {str(e)}", 400)

        session.refresh(order)
        return OrderOutSchema().dump(order), 201


@blp.route("/<int:order_id>")
class OrderDetailView(MethodView):
    @jwt_required()
    def get(self, order_id: int):
        """Get order detail (must belong to the user)."""
        identity = get_jwt_identity()
        session = current_app.session
        order = session.query(Order).get(order_id)
        if not order or order.user_id != identity["id"]:
            return error_response("Order not found.", 404)
        return OrderOutSchema().dump(order), 200
