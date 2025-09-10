from marshmallow import Schema, fields


class UserOutSchema(Schema):
    id = fields.Int()
    email = fields.Email()
    full_name = fields.String()
    is_active = fields.Boolean()
    role = fields.Function(lambda obj: obj.role.value if hasattr(obj, "role") and obj.role else None)


class UserUpdateSchema(Schema):
    full_name = fields.String()
    password = fields.String(load_only=True)
