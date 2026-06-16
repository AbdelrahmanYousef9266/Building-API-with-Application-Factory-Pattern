# Mechanic Shop API

## Description
A RESTful API for managing a mechanic shop built with Flask using the Application Factory Pattern. Supports managing customers, mechanics, service tickets, and inventory parts with many-to-many relationships, JWT authentication, rate limiting, caching, pagination, Swagger documentation, and unit testing.

## Technologies Used
- **Python** + **Flask** — web framework
- **Flask-SQLAlchemy** — ORM for database models
- **Flask-Marshmallow** + **marshmallow-sqlalchemy** — serialization and validation
- **MySQL** — relational database
- **mysql-connector-python** — MySQL driver
- **Flask-Limiter** — rate limiting
- **Flask-Caching** — response caching
- **python-jose** — JWT token encoding and decoding
- **flask-swagger** — Swagger spec support
- **flask-swagger-ui** — Swagger UI interface

## Setup Instructions

### 1. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create the MySQL Database
Log in to MySQL and run:
```sql
CREATE DATABASE mechanic_shop_db;
```

### 4. Configure the Database Password
Open `app/__init__.py` and update the `SQLALCHEMY_DATABASE_URI` with your MySQL credentials.

### 5. Run the App
```bash
python app.py
```
Tables are created automatically on first run. The server starts at `http://127.0.0.1:5000`.

---

## Documentation

### Swagger UI
Interactive API documentation is available at:

```
http://127.0.0.1:5000/api/docs
```

The raw OpenAPI JSON spec is available at:

```
http://127.0.0.1:5000/api/swagger.json
```

### How to Use Swagger UI
1. Start the app with `python app.py`
2. Open your browser and go to `http://127.0.0.1:5000/api/docs`
3. Expand any endpoint to see its description, parameters, and example request/response
4. For token-protected routes, first use `POST /customers/login` to get a JWT token, then click **Authorize** (lock icon) and enter `Bearer <your_token>`
5. Click **Try it out** on any endpoint to send live requests

### Swagger Setup Notes
- The spec is defined in `app/swagger.py` as a Python dictionary
- Two blueprints are registered in `app/__init__.py`: one serving the JSON spec and one serving the UI
- The spec follows **OpenAPI 2.0 (Swagger 2.0)** format

---

## Testing

### How to Run Tests
From the project root directory, run:

```bash
python -m unittest discover tests
```

To run a specific test file:
```bash
python -m unittest tests.test_customers
python -m unittest tests.test_mechanics
python -m unittest tests.test_service_tickets
python -m unittest tests.test_inventory
```

To run a specific test case:
```bash
python -m unittest tests.test_customers.TestCustomers.test_create_customer_success
```

### Test Configuration
- Tests use **SQLite in-memory** database — the production MySQL database is never touched
- Rate limiting is **disabled** during tests
- Each test creates a fresh database and tears it down after, so tests are fully isolated
- The shared test configuration lives in `tests/base.py`

### Test Coverage
Each test file covers both **positive** (success) and **negative** (error) cases:

| File | Routes Tested |
|------|--------------|
| `tests/test_customers.py` | POST, GET, PUT, DELETE `/customers/`, login, my-tickets |
| `tests/test_mechanics.py` | POST, GET, PUT, DELETE `/mechanics/`, most-tickets |
| `tests/test_service_tickets.py` | POST, GET `/service-tickets/`, assign, remove, edit, add-part |
| `tests/test_inventory.py` | POST, GET, PUT, DELETE `/inventory/` |

---

## Advanced Features

### Rate Limiting
- `GET /customers/` is limited to **5 requests per minute**.
- A default limit of **200 per day / 50 per hour** applies to all routes.
- Returns HTTP 429 with a plain-text message when exceeded.

### Caching
- `GET /mechanics/` is cached for **60 seconds** using SimpleCache (in-memory).
- Subsequent requests within 60 seconds return the cached response without hitting the database.

### Token Authentication
- `POST /customers/login` returns a signed JWT token (valid for 1 hour).
- Protected routes require the header: `Authorization: Bearer <token>`
- Decoded payload contains `customer_id` which is injected into the route function.
- Error responses: 401 with a JSON `{"error": "..."}` message for missing, invalid, or expired tokens.

### Pagination
- `GET /customers/` supports `?page=1&per_page=5` query parameters.
- Response includes `customers`, `page`, `per_page`, `total`, and `pages`.

---

## API Endpoints

### Customers — `/customers`
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/customers/` | No | Create a new customer |
| GET | `/customers/` | No | Get all customers (paginated, rate limited) |
| GET | `/customers/<id>` | No | Get customer by ID |
| PUT | `/customers/<id>` | No | Update customer by ID |
| DELETE | `/customers/<id>` | No | Delete customer by ID |
| POST | `/customers/login` | No | Login and receive JWT token |
| GET | `/customers/my-tickets` | **JWT** | Get service tickets for logged-in customer |

**POST /customers/ body:**
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-1234",
  "address": "123 Main St",
  "password": "mypassword123"
}
```

**POST /customers/login body:**
```json
{
  "email": "john@example.com",
  "password": "mypassword123"
}
```

**GET /customers/ with pagination:**
```
GET /customers/?page=1&per_page=5
```

**GET /customers/my-tickets — Authorization header:**
```
Authorization: Bearer <your_jwt_token>
```

---

### Mechanics — `/mechanics`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mechanics/` | Create a new mechanic |
| GET | `/mechanics/` | Get all mechanics (cached 60s) |
| GET | `/mechanics/<id>` | Get mechanic by ID |
| PUT | `/mechanics/<id>` | Update mechanic by ID |
| DELETE | `/mechanics/<id>` | Delete mechanic by ID |
| GET | `/mechanics/most-tickets` | Mechanics ranked by ticket count |

**POST /mechanics/ body:**
```json
{
  "name": "Jane Doe",
  "email": "jane@shop.com",
  "phone": "555-5678",
  "address": "456 Garage Ave",
  "salary": 55000.00
}
```

---

### Service Tickets — `/service-tickets`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/service-tickets/` | Create a new service ticket |
| GET | `/service-tickets/` | Get all service tickets |
| PUT | `/service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` | Assign mechanic to ticket |
| PUT | `/service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` | Remove mechanic from ticket |
| PUT | `/service-tickets/<ticket_id>/edit` | Bulk add/remove mechanics |
| PUT | `/service-tickets/<ticket_id>/add-part/<inventory_id>` | Add inventory part to ticket |

**POST /service-tickets/ body:**
```json
{
  "customer_id": 1,
  "vin": "1HGBH41JXMN109186",
  "service_description": "Oil change and tire rotation",
  "status": "open"
}
```

**PUT /service-tickets/<id>/edit body:**
```json
{
  "add_ids": [1, 2],
  "remove_ids": [3]
}
```

---

### Inventory — `/inventory`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/inventory/` | Create a new inventory part |
| GET | `/inventory/` | Get all inventory parts |
| GET | `/inventory/<id>` | Get inventory part by ID |
| PUT | `/inventory/<id>` | Update inventory part by ID |
| DELETE | `/inventory/<id>` | Delete inventory part by ID |

**POST /inventory/ body:**
```json
{
  "name": "Oil Filter",
  "price": 12.99
}
```

---

## Postman Testing Order

Test in this order to avoid dependency errors:

1. **POST /mechanics/** — Create 2–3 mechanics
2. **POST /customers/** — Create a customer (include `password`)
3. **POST /customers/login** — Login to get JWT token
4. **POST /service-tickets/** — Create a service ticket using `customer_id`
5. **POST /inventory/** — Create inventory parts
6. **PUT /service-tickets/<id>/assign-mechanic/<id>** — Assign a mechanic
7. **PUT /service-tickets/<id>/edit** — Bulk edit mechanic assignments
8. **PUT /service-tickets/<id>/add-part/<id>** — Add inventory part to ticket
9. **GET /customers/my-tickets** — Use the JWT token in Authorization header
10. **GET /customers/** — Test pagination with `?page=1&per_page=5`
11. **GET /mechanics/most-tickets** — See ranking by ticket count
12. **GET /mechanics/** — Make the same request 3× within 60s to confirm caching

---

## Database Relationships (ERD)

### Customer → Service Ticket
- One Customer can have many Service Tickets (One-to-Many)

### Service Ticket ↔ Mechanic
- Many-to-Many via `service_ticket_mechanics` association table

### Service Ticket ↔ Inventory
- Many-to-Many via `service_ticket_inventory` association table

### Entity Overview

**Customer** — id, name, email, phone, address, password

**Mechanic** — id, name, email, phone, address, salary

**ServiceTicket** — id, customer_id, vin, service_description, status, created_at

**Inventory** — id, name, price

---

---

## Environment Variables

The application uses environment variables for sensitive configuration in production. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `DATABASE_URI` | Full PostgreSQL connection string (provided by Render) |
| `SECRET_KEY` | Secret key used to sign JWT tokens |

`.env` is listed in `.gitignore` and must never be committed to source control.

---

## Render Deployment

### Live URL
```
https://my-api-name.onrender.com
```
Replace `my-api-name` with your actual Render service name after deployment.

### Steps to Deploy on Render

1. Push this repository to GitHub.
2. Go to [https://render.com](https://render.com) and sign in.
3. Click **New → Web Service** and connect your GitHub repository.
4. Configure the service:
   - **Name:** `mechanic-shop-api` (or your preferred name)
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn flask_app:app`
5. Under **Environment Variables**, add:
   - `DATABASE_URI` — your PostgreSQL connection string
   - `SECRET_KEY` — a strong random secret
6. Under **Advanced**, add a **PostgreSQL** database if you don't already have one (Render will provide the `DATABASE_URI` automatically when linked).
7. Click **Create Web Service**. Render will build and deploy automatically.

### Swagger UI on Render
After deploying, open:
```
https://my-api-name.onrender.com/api/docs
```
Update `SWAGGER_HOST` in [app/swagger.py](app/swagger.py) to match your actual Render service name.

---

## CI/CD Pipeline (GitHub Actions)

The workflow file is at [.github/workflows/main.yaml](.github/workflows/main.yaml).

### Pipeline Stages

| Job | Trigger | What it does |
|-----|---------|--------------|
| `build` | Push to `main` | Checks out code, sets up Python 3.11, installs dependencies |
| `test` | After `build` | Runs `python -m unittest discover tests` against an SQLite in-memory DB |
| `deploy` | After `test` passes | Calls the Render Deploy API to trigger a new deployment |

### GitHub Secrets Required

Go to your GitHub repository → **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Where to find it |
|--------|-----------------|
| `RENDER_API_KEY` | Render dashboard → Account → API Keys |
| `SERVICE_ID` | Render dashboard → your service → Settings → Service ID (starts with `srv-`) |

### How to Verify CI/CD is Working

1. Push any commit to the `main` branch.
2. Go to your GitHub repository → **Actions** tab.
3. You should see a workflow run with three jobs: `build → test → deploy`.
4. If all three pass (green), a new deployment is triggered on Render automatically.
5. Check the **Render dashboard → your service → Events** tab to confirm the deploy was received.

---

## Author

**Abdelrahman Yousef**

GitHub: https://github.com/AbdelrahmanYousef9266
