from marshmallow import Schema, fields


class ProductImageSchema(Schema):
    id = fields.Int(dump_only=True)
    url = fields.String(required=True)
    alt_text = fields.String(load_default=None)


class ProductInventorySchema(Schema):
    quantity = fields.Int(required=True)


class ProductInSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(load_default=None)
    price = fields.Decimal(required=True, as_string=True)
    category_id = fields.Int(load_default=None)
    images = fields.List(fields.Nested(ProductImageSchema), load_default=[])
    inventory = fields.Nested(ProductInventorySchema, load_default=None)


class ProductOutSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String(allow_none=True)
    price = fields.Decimal(as_string=True)
    category_id = fields.Int(allow_none=True)
    images = fields.List(fields.Nested(ProductImageSchema))
    inventory = fields.Nested(ProductInventorySchema, allow_none=True)
