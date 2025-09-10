from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.session import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    products = relationship("Product", back_populates="category", cascade="all, delete", passive_deletes=True)
