from marshmallow import Schema, fields


class CategoryInSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(load_default=None)


class CategoryOutSchema(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String(allow_none=True)
