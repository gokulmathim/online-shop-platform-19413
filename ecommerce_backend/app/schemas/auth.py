from marshmallow import Schema, fields


class SignupSchema(Schema):
    email = fields.Email(required=True, description="User email")
    password = fields.String(required=True, load_only=True, description="User password")
    full_name = fields.String(required=True, description="Full name")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


class TokenSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
