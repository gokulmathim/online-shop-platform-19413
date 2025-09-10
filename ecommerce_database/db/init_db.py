"""
Database initialization utilities.

- Creates tables if they do not exist (for simple setups or SQLite dev).
- Optionally seeds demo data for local development.

Usage:
    python -m db.init_db --seed
"""
import argparse
from sqlalchemy.exc import SQLAlchemyError
from .session import Base, engine, get_session
from ..models import (
    User, UserRole, Category, Product, ProductImage, ProductInventory,
    Cart, CartItem, Address, Order, OrderItem, OrderStatus, Payment, PaymentMethod, PaymentStatus
)

def create_all():
    """Create all tables based on SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)

def seed_demo():
    """Insert small demo dataset."""
    session = get_session()
    try:
        # Users
        user = User(email="john@example.com", password_hash="hashed:demo", full_name="John Doe", role=UserRole.CUSTOMER)
        admin = User(email="admin@example.com", password_hash="hashed:admin", full_name="Admin User", role=UserRole.ADMIN)
        session.add_all([user, admin])

        # Categories
        cat1 = Category(name="Electronics", description="Gadgets and devices")
        cat2 = Category(name="Books", description="Printed and digital books")
        session.add_all([cat1, cat2])
        session.flush()

        # Products
        p1 = Product(name="Smartphone X", description="A powerful smartphone", price=699.99, category=cat1)
        p2 = Product(name="Wireless Headphones", description="Noise-cancelling", price=199.99, category=cat1)
        p3 = Product(name="Sci-Fi Novel", description="A thrilling space adventure", price=14.99, category=cat2)
        session.add_all([p1, p2, p3])
        session.flush()

        # Inventory
        session.add_all([
            ProductInventory(product=p1, quantity=50),
            ProductInventory(product=p2, quantity=120),
            ProductInventory(product=p3, quantity=500),
        ])

        # Images
        session.add_all([
            ProductImage(product=p1, url="https://example.com/img/phone.jpg", alt_text="Smartphone"),
            ProductImage(product=p2, url="https://example.com/img/headphones.jpg", alt_text="Headphones"),
            ProductImage(product=p3, url="https://example.com/img/book.jpg", alt_text="Book"),
        ])

        # Address
        addr = Address(user=user, line1="123 Main St", city="Metropolis", state="NY", postal_code="12345", country="USA", is_default_shipping=True, is_default_billing=True)
        session.add(addr)
        session.flush()

        # Cart
        cart = Cart(user=user)
        session.add(cart)
        session.flush()

        # Cart Items
        session.add_all([
            CartItem(cart=cart, product=p1, quantity=1, unit_price=p1.price),
            CartItem(cart=cart, product=p3, quantity=2, unit_price=p3.price),
        ])

        # Order
        order = Order(
            user=user,
            shipping_address_id=addr.id,
            billing_address_id=addr.id,
            status=OrderStatus.PENDING,
            subtotal_amount= p1.price * 1 + p3.price * 2,
            shipping_amount=9.99,
            tax_amount=5.50,
            total_amount= (p1.price * 1 + p3.price * 2) + 9.99 + 5.50
        )
        session.add(order)
        session.flush()

        # Order Items
        session.add_all([
            OrderItem(order=order, product=p1, product_name=p1.name, unit_price=p1.price, quantity=1, line_total=p1.price * 1),
            OrderItem(order=order, product=p3, product_name=p3.name, unit_price=p3.price, quantity=2, line_total=p3.price * 2),
        ])

        # Payment
        payment = Payment(order=order, user=user, method=PaymentMethod.STRIPE, status=PaymentStatus.PENDING, amount=order.total_amount, currency="USD", provider_charge_id=None)
        session.add(payment)

        session.commit()
        print("Seed data inserted.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Failed to seed demo data: {e}")
        raise
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description="Initialize ecommerce database.")
    parser.add_argument("--seed", action="store_true", help="Seed demo data after creating tables")
    args = parser.parse_args()

    print("Creating tables (if not exist)...")
    create_all()
    if args.seed:
        print("Seeding demo data...")
        seed_demo()
    print("Done.")

if __name__ == "__main__":
    main()
