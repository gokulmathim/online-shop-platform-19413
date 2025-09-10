# E-commerce Backend (Flask)

This Flask backend provides REST APIs for authentication, users, categories, products, cart, orders, and mock payments. It connects to the `ecommerce_database` package for SQLAlchemy models and sessions.

## Features
- JWT authentication (signup, login, me)
- Users: profile read/update; admin list
- Categories: list/get/create/update/delete (admin for write)
- Products: list/get/create/update/delete (admin for write)
- Cart: view, add/update/remove items, clear
- Orders: create from payload or from cart, list, retrieve
- Payments: mock processing that authorizes/captures immediately
- OpenAPI docs via flask-smorest at `/docs/`

## Configuration
Copy `.env.example` to `.env` and adjust values. Important keys:
- SECRET_KEY, JWT_SECRET_KEY
- DATABASE_URL (shared with ecommerce_database)
- See `.env.example` for details.

## Running
- Install dependencies:
  - pip install -r requirements.txt
  - and ensure `ecommerce_database` dependencies are installed (or installed as editable package in the environment).
- Make sure the database is ready (apply migrations / create tables). For SQLite example:
  - In ecommerce_database: `python -m db.init_db --seed`
- Start backend:
  - `python run.py`
  - Access docs: `http://localhost:3001/docs/`

## OpenAPI
- Generate `interfaces/openapi.json`:
  - `python generate_openapi.py`

## Notes
- This backend expects the `ecommerce_database` Python package to be importable (PYTHONPATH should include the path to that container).
