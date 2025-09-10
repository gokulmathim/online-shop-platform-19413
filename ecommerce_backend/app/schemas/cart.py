from marshmallow import Schema, fields


class CartItemInSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)


class CartItemOutSchema(Schema):
    id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()
    unit_price = fields.Decimal(as_string=True)


class CartOutSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    items = fields.List(fields.Nested(CartItemOutSchema))
