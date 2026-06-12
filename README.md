# Mechanic Shop API

## Description
A RESTful API for managing a mechanic shop built with Flask using the Application Factory Pattern. It supports managing customers, mechanics, and service tickets with many-to-many mechanic assignments.

## Technologies Used
- **Python** + **Flask** — web framework
- **Flask-SQLAlchemy** — ORM for database models
- **Flask-Marshmallow** + **marshmallow-sqlalchemy** — serialization and validation
- **MySQL** — relational database
- **mysql-connector-python** — MySQL driver

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
Open `app/__init__.py` and replace `<YOUR MYSQL PASSWORD>` with your actual MySQL root password.

### 5. Run the App
```bash
python app.py
```
Tables will be created automatically on first run. The server starts at `http://127.0.0.1:5000`.

---

## API Endpoints

### Customers — `/customers`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers/` | Create a new customer |
| GET | `/customers/` | Get all customers |
| GET | `/customers/<id>` | Get customer by ID |
| PUT | `/customers/<id>` | Update customer by ID |
| DELETE | `/customers/<id>` | Delete customer by ID |

**Sample POST body:**
```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-1234",
  "address": "123 Main St"
}
```

---

### Mechanics — `/mechanics`
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mechanics/` | Create a new mechanic |
| GET | `/mechanics/` | Get all mechanics |
| GET | `/mechanics/<id>` | Get mechanic by ID |
| PUT | `/mechanics/<id>` | Update mechanic by ID |
| DELETE | `/mechanics/<id>` | Delete mechanic by ID |

**Sample POST body:**
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

**Sample POST body:**
```json
{
  "customer_id": 1,
  "vin": "1HGBH41JXMN109186",
  "service_description": "Oil change and tire rotation",
  "status": "open"
}
```

---

## Author
**Abdelrahman Yousef**
