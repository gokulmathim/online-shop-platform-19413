from datetime import datetime
from enum import Enum
from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.session import Base

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    shipping_address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    billing_address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="orders")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    line_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
