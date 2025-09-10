"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # enums
    userrole = sa.Enum("customer", "admin", name="userrole")
    orderstatus = sa.Enum("pending", "paid", "shipped", "delivered", "canceled", "refunded", name="orderstatus")
    paymentstatus = sa.Enum("pending", "authorized", "captured", "failed", "refunded", name="paymentstatus")
    paymentmethod = sa.Enum("card", "paypal", "stripe", name="paymentmethod")

    userrole.create(op.get_bind(), checkfirst=True)
    orderstatus.create(op.get_bind(), checkfirst=True)
    paymentstatus.create(op.get_bind(), checkfirst=True)
    paymentmethod.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("role", userrole, nullable=False, server_default="customer"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("description", sa.String(length=500), nullable=True),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
    )
    op.create_index("ix_products_name", "products", ["name"], unique=False)

    op.create_table(
        "product_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("alt_text", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "product_inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), unique=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("line1", sa.String(length=255), nullable=False),
        sa.Column("line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=30), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column("is_default_shipping", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("is_default_billing", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
    )

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("shipping_address_id", sa.Integer(), sa.ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("billing_address_id", sa.Integer(), sa.ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", orderstatus, nullable=False, server_default="pending"),
        sa.Column("subtotal_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("shipping_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("method", paymentmethod, nullable=False),
        sa.Column("status", paymentstatus, nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("provider_charge_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("(CURRENT_TIMESTAMP)")),
    )

def downgrade():
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("addresses")
    op.drop_table("product_inventory")
    op.drop_table("product_images")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    # drop enums
    bind = op.get_bind()
    sa.Enum(name="userrole").drop(bind, checkfirst=True)
    sa.Enum(name="orderstatus").drop(bind, checkfirst=True)
    sa.Enum(name="paymentstatus").drop(bind, checkfirst=True)
    sa.Enum(name="paymentmethod").drop(bind, checkfirst=True)
