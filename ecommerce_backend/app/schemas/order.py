from marshmallow import Schema, fields


class OrderItemInSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)


class OrderCreateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemInSchema), required=True, description="Items to order")
    shipping_address_id = fields.Int(load_default=None)
    billing_address_id = fields.Int(load_default=None)


class OrderItemOutSchema(Schema):
    id = fields.Int()
    product_id = fields.Int(allow_none=True)
    product_name = fields.String()
    unit_price = fields.Decimal(as_string=True)
    quantity = fields.Int()
    line_total = fields.Decimal(as_string=True)


class OrderOutSchema(Schema):
    id = fields.Int()
    user_id = fields.Int(allow_none=True)
    status = fields.Function(lambda obj: obj.status.value if obj.status else None)
    subtotal_amount = fields.Decimal(as_string=True)
    shipping_amount = fields.Decimal(as_string=True)
    tax_amount = fields.Decimal(as_string=True)
    total_amount = fields.Decimal(as_string=True)
    items = fields.List(fields.Nested(OrderItemOutSchema))
