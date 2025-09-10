from marshmallow import Schema, fields


class PaymentCreateSchema(Schema):
    order_id = fields.Int(required=True)
    method = fields.String(required=True, description="Payment method (mock supports: card, paypal, stripe)")
    amount = fields.Decimal(required=True, as_string=True)
    currency = fields.String(load_default="USD")


class PaymentOutSchema(Schema):
    id = fields.Int()
    order_id = fields.Int(allow_none=True)
    user_id = fields.Int(allow_none=True)
    method = fields.String()
    status = fields.String()
    amount = fields.Decimal(as_string=True)
    currency = fields.String()
    provider_charge_id = fields.String(allow_none=True)
