from datetime import datetime
from enum import Enum
from sqlalchemy import Integer, ForeignKey, DateTime, Numeric, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.session import Base

class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    CARD = "card"
    PAYPAL = "paypal"
    STRIPE = "stripe"  # logical placeholder

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    method: Mapped[PaymentMethod] = mapped_column(SAEnum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    provider_charge_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="payments")
    user = relationship("User", back_populates="payments")
