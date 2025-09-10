from uuid import uuid4
from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from ecommerce_database.models import Payment, PaymentStatus, PaymentMethod, Order
from ..schemas.payment import PaymentCreateSchema, PaymentOutSchema
from ..utils.common import error_response

blp = Blueprint("Payments", "payments", url_prefix="/payments", description="Payment processing (mock)")


def _map_method(method_str: str) -> PaymentMethod:
    m = method_str.lower()
    if m == "card":
        return PaymentMethod.CARD
    if m == "paypal":
        return PaymentMethod.PAYPAL
    if m == "stripe":
        return PaymentMethod.STRIPE
    raise ValueError("Unsupported payment method")


@blp.route("")
class PaymentCreateView(MethodView):
    @jwt_required()
    def post(self):
        """Mock payment processing. Creates payment tied to an order."""
        identity = get_jwt_identity()
        session = current_app.session
        data = PaymentCreateSchema().load(request.json or {})

        order = session.query(Order).get(data["order_id"])
        if not order or order.user_id != identity["id"]:
            return error_response("Order not found.", 404)

        try:
            method = _map_method(data["method"])
            payment = Payment(
                order_id=order.id,
                user_id=identity["id"],
                method=method,
                status=PaymentStatus.AUTHORIZED,  # mock immediate auth
                amount=data["amount"],
                currency=data.get("currency") or current_app.config.get("PAYMENT_CURRENCY", "USD"),
                provider_charge_id=str(uuid4()),
            )
            session.add(payment)
            # In a real system, call provider and update status based on result
            # We'll mark as CAPTURED if amount matches order total
            if str(data["amount"]) == str(order.total_amount):
                payment.status = PaymentStatus.CAPTURED
                order.status = order.status.PAID
            session.commit()
        except (ValueError, SQLAlchemyError) as e:
            session.rollback()
            return error_response(f"Payment failed: {str(e)}", 400)

        return PaymentOutSchema().dump(payment), 201


@blp.route("/<int:payment_id>")
class PaymentDetailView(MethodView):
    @jwt_required()
    def get(self, payment_id: int):
        """Get payment detail (must belong to the user)."""
        identity = get_jwt_identity()
        session = current_app.session
        payment = session.query(Payment).get(payment_id)
        if not payment or payment.user_id != identity["id"]:
            return error_response("Payment not found.", 404)
        return PaymentOutSchema().dump(payment), 200
