from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

# URL where Swagger UI is served
SWAGGER_URL = "/api/docs"

# URL where the raw JSON spec is served
API_URL = "/api/swagger.json"

# ── Swagger host configuration ─────────────────────────────────────────────────
# Local development:  "127.0.0.1:5000"
# Render production:  "my-api-name.onrender.com"  ← replace with your service name
SWAGGER_HOST = "my-api-name.onrender.com"
SWAGGER_SCHEMES = ["https"]

# ── Full OpenAPI 2.0 (Swagger) Specification ──────────────────────────────────
SWAGGER_SPEC = {
    "swagger": "2.0",
    "info": {
        "title": "Mechanic Shop API",
        "description": (
            "A RESTful API for managing a mechanic shop. "
            "Supports customers, mechanics, service tickets, and inventory "
            "with JWT authentication, rate limiting, caching, and pagination."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Abdelrahman Yousef",
            "url": "https://github.com/AbdelrahmanYousef9266",
        },
    },
    "host": SWAGGER_HOST,
    "basePath": "/",
    "schemes": SWAGGER_SCHEMES,
    "consumes": ["application/json"],
    "produces": ["application/json"],
    # ── Security ──
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT token as: Bearer <token>",
        }
    },
    # ── Reusable schemas ──
    "definitions": {
        "Customer": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "John Smith"},
                "email": {"type": "string", "format": "email", "example": "john@example.com"},
                "phone": {"type": "string", "example": "555-1234"},
                "address": {"type": "string", "example": "123 Main St"},
            },
        },
        "CustomerInput": {
            "type": "object",
            "required": ["name", "email", "phone", "address", "password"],
            "properties": {
                "name": {"type": "string", "example": "John Smith"},
                "email": {"type": "string", "format": "email", "example": "john@example.com"},
                "phone": {"type": "string", "example": "555-1234"},
                "address": {"type": "string", "example": "123 Main St"},
                "password": {"type": "string", "example": "mypassword123"},
            },
        },
        "Mechanic": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Jane Doe"},
                "email": {"type": "string", "format": "email", "example": "jane@shop.com"},
                "phone": {"type": "string", "example": "555-5678"},
                "address": {"type": "string", "example": "456 Garage Ave"},
                "salary": {"type": "number", "format": "float", "example": 55000.00},
            },
        },
        "MechanicInput": {
            "type": "object",
            "required": ["name", "email", "phone", "address", "salary"],
            "properties": {
                "name": {"type": "string", "example": "Jane Doe"},
                "email": {"type": "string", "format": "email", "example": "jane@shop.com"},
                "phone": {"type": "string", "example": "555-5678"},
                "address": {"type": "string", "example": "456 Garage Ave"},
                "salary": {"type": "number", "format": "float", "example": 55000.00},
            },
        },
        "ServiceTicket": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "vin": {"type": "string", "example": "1HGBH41JXMN109186"},
                "service_description": {"type": "string", "example": "Oil change and tire rotation"},
                "status": {"type": "string", "example": "open"},
                "created_at": {"type": "string", "format": "date-time", "example": "2024-01-15T10:30:00"},
                "customer_id": {"type": "integer", "example": 1},
                "mechanic_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [1, 2],
                },
                "inventory_part_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [3],
                },
            },
        },
        "ServiceTicketInput": {
            "type": "object",
            "required": ["vin", "service_description", "customer_id"],
            "properties": {
                "vin": {"type": "string", "example": "1HGBH41JXMN109186"},
                "service_description": {"type": "string", "example": "Oil change and tire rotation"},
                "status": {"type": "string", "example": "open", "default": "open"},
                "customer_id": {"type": "integer", "example": 1},
            },
        },
        "EditMechanicAssignments": {
            "type": "object",
            "properties": {
                "add_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [1, 2],
                    "description": "Mechanic IDs to add to the ticket",
                },
                "remove_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "example": [3],
                    "description": "Mechanic IDs to remove from the ticket",
                },
            },
        },
        "Inventory": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "example": 1},
                "name": {"type": "string", "example": "Oil Filter"},
                "price": {"type": "number", "format": "float", "example": 12.99},
            },
        },
        "InventoryInput": {
            "type": "object",
            "required": ["name", "price"],
            "properties": {
                "name": {"type": "string", "example": "Oil Filter"},
                "price": {"type": "number", "format": "float", "example": 12.99},
            },
        },
        "LoginRequest": {
            "type": "object",
            "required": ["email", "password"],
            "properties": {
                "email": {"type": "string", "format": "email", "example": "john@example.com"},
                "password": {"type": "string", "example": "mypassword123"},
            },
        },
        "LoginResponse": {
            "type": "object",
            "properties": {
                "token": {
                    "type": "string",
                    "example": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                },
                "message": {"type": "string", "example": "Login successful"},
            },
        },
        "PaginationResponse": {
            "type": "object",
            "properties": {
                "customers": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Customer"},
                },
                "page": {"type": "integer", "example": 1},
                "per_page": {"type": "integer", "example": 5},
                "total": {"type": "integer", "example": 25},
                "pages": {"type": "integer", "example": 5},
            },
        },
        "Error": {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Resource not found"},
            },
        },
        "Message": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Operation completed successfully"},
            },
        },
    },
    # ── Route Paths ──
    "paths": {
        # ── CUSTOMERS ─────────────────────────────────────────────────────────
        "/customers/": {
            "post": {
                "tags": ["Customers"],
                "summary": "Create a new customer",
                "description": "Registers a new customer account. The password is stored and never returned in responses.",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/CustomerInput"},
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Customer created successfully",
                        "schema": {"$ref": "#/definitions/Customer"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "name": "John Smith",
                                "email": "john@example.com",
                                "phone": "555-1234",
                                "address": "123 Main St",
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error — missing or invalid fields",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            },
            "get": {
                "tags": ["Customers"],
                "summary": "Get all customers (paginated)",
                "description": (
                    "Returns a paginated list of all customers. "
                    "Rate limited to 5 requests per minute. "
                    "Use ?page and ?per_page query parameters to control pagination."
                ),
                "parameters": [
                    {
                        "in": "query",
                        "name": "page",
                        "type": "integer",
                        "default": 1,
                        "description": "Page number to retrieve",
                    },
                    {
                        "in": "query",
                        "name": "per_page",
                        "type": "integer",
                        "default": 5,
                        "description": "Number of customers per page",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Paginated list of customers",
                        "schema": {"$ref": "#/definitions/PaginationResponse"},
                        "examples": {
                            "application/json": {
                                "customers": [
                                    {
                                        "id": 1,
                                        "name": "John Smith",
                                        "email": "john@example.com",
                                        "phone": "555-1234",
                                        "address": "123 Main St",
                                    }
                                ],
                                "page": 1,
                                "per_page": 5,
                                "total": 1,
                                "pages": 1,
                            }
                        },
                    },
                    "429": {"description": "Rate limit exceeded — too many requests"},
                },
            },
        },
        "/customers/{id}": {
            "get": {
                "tags": ["Customers"],
                "summary": "Get a customer by ID",
                "description": "Returns a single customer record by their unique ID.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The customer's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Customer found",
                        "schema": {"$ref": "#/definitions/Customer"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "name": "John Smith",
                                "email": "john@example.com",
                                "phone": "555-1234",
                                "address": "123 Main St",
                            }
                        },
                    },
                    "404": {
                        "description": "Customer not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            },
            "put": {
                "tags": ["Customers"],
                "summary": "Update a customer by ID",
                "description": "Updates all fields for an existing customer. All fields are required.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The customer's unique ID",
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/CustomerInput"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Customer updated successfully",
                        "schema": {"$ref": "#/definitions/Customer"},
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {"description": "Customer not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "delete": {
                "tags": ["Customers"],
                "summary": "Delete a customer by ID",
                "description": "Permanently deletes a customer and all their associated service tickets.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The customer's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Customer deleted successfully",
                        "schema": {"$ref": "#/definitions/Message"},
                        "examples": {
                            "application/json": {"message": "Customer 1 deleted successfully"}
                        },
                    },
                    "404": {"description": "Customer not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
        },
        "/customers/login": {
            "post": {
                "tags": ["Customers"],
                "summary": "Customer login",
                "description": (
                    "Authenticates a customer with email and password. "
                    "Returns a signed JWT token valid for 1 hour. "
                    "Use this token in the Authorization header for protected routes."
                ),
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/LoginRequest"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Login successful — JWT token returned",
                        "schema": {"$ref": "#/definitions/LoginResponse"},
                        "examples": {
                            "application/json": {
                                "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                                "message": "Login successful",
                            }
                        },
                    },
                    "400": {"description": "Missing or invalid request data", "schema": {"$ref": "#/definitions/Error"}},
                    "401": {
                        "description": "Invalid email or password",
                        "schema": {"$ref": "#/definitions/Error"},
                        "examples": {
                            "application/json": {"error": "Invalid email or password"}
                        },
                    },
                },
            }
        },
        "/customers/my-tickets": {
            "get": {
                "tags": ["Customers"],
                "summary": "Get logged-in customer's service tickets",
                "description": (
                    "Returns all service tickets belonging to the authenticated customer. "
                    "Requires a valid JWT token in the Authorization header."
                ),
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {
                        "in": "header",
                        "name": "Authorization",
                        "required": True,
                        "type": "string",
                        "description": "Bearer token: Bearer <your_jwt_token>",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of service tickets for this customer",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/ServiceTicket"},
                        },
                        "examples": {
                            "application/json": [
                                {
                                    "id": 1,
                                    "vin": "1HGBH41JXMN109186",
                                    "service_description": "Oil change",
                                    "status": "open",
                                    "customer_id": 1,
                                    "mechanic_ids": [1],
                                    "inventory_part_ids": [2],
                                }
                            ]
                        },
                    },
                    "401": {
                        "description": "Missing, invalid, or expired token",
                        "schema": {"$ref": "#/definitions/Error"},
                        "examples": {
                            "application/json": {
                                "error": "Missing or invalid Authorization header. Use: Bearer <token>"
                            }
                        },
                    },
                    "404": {"description": "Customer not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            }
        },
        # ── MECHANICS ─────────────────────────────────────────────────────────
        "/mechanics/": {
            "post": {
                "tags": ["Mechanics"],
                "summary": "Create a new mechanic",
                "description": "Registers a new mechanic employee in the system.",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/MechanicInput"},
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Mechanic created successfully",
                        "schema": {"$ref": "#/definitions/Mechanic"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "name": "Jane Doe",
                                "email": "jane@shop.com",
                                "phone": "555-5678",
                                "address": "456 Garage Ave",
                                "salary": 55000.0,
                            }
                        },
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "get": {
                "tags": ["Mechanics"],
                "summary": "Get all mechanics",
                "description": (
                    "Returns a list of all mechanics. "
                    "Response is cached for 60 seconds — repeated requests within that window "
                    "are served from cache without hitting the database."
                ),
                "responses": {
                    "200": {
                        "description": "List of all mechanics",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/Mechanic"},
                        },
                        "examples": {
                            "application/json": [
                                {
                                    "id": 1,
                                    "name": "Jane Doe",
                                    "email": "jane@shop.com",
                                    "phone": "555-5678",
                                    "address": "456 Garage Ave",
                                    "salary": 55000.0,
                                }
                            ]
                        },
                    }
                },
            },
        },
        "/mechanics/{id}": {
            "get": {
                "tags": ["Mechanics"],
                "summary": "Get a mechanic by ID",
                "description": "Returns a single mechanic record by their unique ID.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The mechanic's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Mechanic found",
                        "schema": {"$ref": "#/definitions/Mechanic"},
                    },
                    "404": {"description": "Mechanic not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "put": {
                "tags": ["Mechanics"],
                "summary": "Update a mechanic by ID",
                "description": "Updates all fields for an existing mechanic. All fields are required.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The mechanic's unique ID",
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/MechanicInput"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Mechanic updated successfully",
                        "schema": {"$ref": "#/definitions/Mechanic"},
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {"description": "Mechanic not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "delete": {
                "tags": ["Mechanics"],
                "summary": "Delete a mechanic by ID",
                "description": "Permanently deletes a mechanic from the system.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The mechanic's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Mechanic deleted successfully",
                        "schema": {"$ref": "#/definitions/Message"},
                        "examples": {
                            "application/json": {"message": "Mechanic 1 deleted successfully"}
                        },
                    },
                    "404": {"description": "Mechanic not found", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
        },
        "/mechanics/most-tickets": {
            "get": {
                "tags": ["Mechanics"],
                "summary": "Get mechanics ranked by service ticket count",
                "description": (
                    "Returns all mechanics ordered by the number of service tickets "
                    "they have worked on (descending). Each record includes a ticket_count field."
                ),
                "responses": {
                    "200": {
                        "description": "Mechanics ranked by ticket count",
                        "schema": {
                            "type": "array",
                            "items": {
                                "allOf": [
                                    {"$ref": "#/definitions/Mechanic"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "ticket_count": {
                                                "type": "integer",
                                                "example": 5,
                                            }
                                        },
                                    },
                                ]
                            },
                        },
                        "examples": {
                            "application/json": [
                                {
                                    "id": 1,
                                    "name": "Jane Doe",
                                    "email": "jane@shop.com",
                                    "phone": "555-5678",
                                    "address": "456 Garage Ave",
                                    "salary": 55000.0,
                                    "ticket_count": 5,
                                }
                            ]
                        },
                    }
                },
            }
        },
        # ── SERVICE TICKETS ───────────────────────────────────────────────────
        "/service-tickets/": {
            "post": {
                "tags": ["Service Tickets"],
                "summary": "Create a new service ticket",
                "description": (
                    "Creates a new service ticket linked to an existing customer. "
                    "The customer must exist before creating a ticket."
                ),
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/ServiceTicketInput"},
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Service ticket created successfully",
                        "schema": {"$ref": "#/definitions/ServiceTicket"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "vin": "1HGBH41JXMN109186",
                                "service_description": "Oil change and tire rotation",
                                "status": "open",
                                "customer_id": 1,
                                "mechanic_ids": [],
                                "inventory_part_ids": [],
                            }
                        },
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "get": {
                "tags": ["Service Tickets"],
                "summary": "Get all service tickets",
                "description": "Returns a list of all service tickets with their assigned mechanics and parts.",
                "responses": {
                    "200": {
                        "description": "List of all service tickets",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/ServiceTicket"},
                        },
                    }
                },
            },
        },
        "/service-tickets/{ticket_id}/assign-mechanic/{mechanic_id}": {
            "put": {
                "tags": ["Service Tickets"],
                "summary": "Assign a mechanic to a service ticket",
                "description": (
                    "Assigns an existing mechanic to an existing service ticket. "
                    "Has no effect if the mechanic is already assigned."
                ),
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_id",
                        "required": True,
                        "type": "integer",
                        "description": "The service ticket's unique ID",
                    },
                    {
                        "in": "path",
                        "name": "mechanic_id",
                        "required": True,
                        "type": "integer",
                        "description": "The mechanic's unique ID",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Mechanic assigned (or already assigned)",
                        "schema": {"$ref": "#/definitions/Message"},
                        "examples": {
                            "application/json": {
                                "message": "Mechanic Jane Doe assigned to ticket 1"
                            }
                        },
                    },
                    "404": {
                        "description": "Service ticket or mechanic not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            }
        },
        "/service-tickets/{ticket_id}/remove-mechanic/{mechanic_id}": {
            "put": {
                "tags": ["Service Tickets"],
                "summary": "Remove a mechanic from a service ticket",
                "description": "Removes an assigned mechanic from a service ticket.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_id",
                        "required": True,
                        "type": "integer",
                        "description": "The service ticket's unique ID",
                    },
                    {
                        "in": "path",
                        "name": "mechanic_id",
                        "required": True,
                        "type": "integer",
                        "description": "The mechanic's unique ID",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Mechanic removed from ticket",
                        "schema": {"$ref": "#/definitions/Message"},
                        "examples": {
                            "application/json": {
                                "message": "Mechanic Jane Doe removed from ticket 1"
                            }
                        },
                    },
                    "400": {
                        "description": "Mechanic is not assigned to this ticket",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                    "404": {
                        "description": "Service ticket or mechanic not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            }
        },
        "/service-tickets/{ticket_id}/edit": {
            "put": {
                "tags": ["Service Tickets"],
                "summary": "Bulk add or remove mechanics from a service ticket",
                "description": (
                    "Adds and/or removes multiple mechanics from a service ticket in one request. "
                    "Provide add_ids with mechanic IDs to assign and remove_ids to unassign."
                ),
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_id",
                        "required": True,
                        "type": "integer",
                        "description": "The service ticket's unique ID",
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/EditMechanicAssignments"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Assignments updated — returns the updated service ticket",
                        "schema": {"$ref": "#/definitions/ServiceTicket"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "vin": "1HGBH41JXMN109186",
                                "service_description": "Oil change",
                                "status": "open",
                                "customer_id": 1,
                                "mechanic_ids": [1, 2],
                                "inventory_part_ids": [],
                            }
                        },
                    },
                    "404": {
                        "description": "Service ticket not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            }
        },
        "/service-tickets/{ticket_id}/add-part/{inventory_id}": {
            "put": {
                "tags": ["Service Tickets"],
                "summary": "Add an inventory part to a service ticket",
                "description": (
                    "Links an inventory part to a service ticket. "
                    "Has no effect if the part is already added."
                ),
                "parameters": [
                    {
                        "in": "path",
                        "name": "ticket_id",
                        "required": True,
                        "type": "integer",
                        "description": "The service ticket's unique ID",
                    },
                    {
                        "in": "path",
                        "name": "inventory_id",
                        "required": True,
                        "type": "integer",
                        "description": "The inventory part's unique ID",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Part added (or already added) — returns the updated ticket",
                        "schema": {"$ref": "#/definitions/ServiceTicket"},
                    },
                    "404": {
                        "description": "Service ticket or inventory part not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            }
        },
        # ── INVENTORY ─────────────────────────────────────────────────────────
        "/inventory/": {
            "post": {
                "tags": ["Inventory"],
                "summary": "Create a new inventory part",
                "description": "Adds a new part to the inventory with a name and price.",
                "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/InventoryInput"},
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Inventory part created successfully",
                        "schema": {"$ref": "#/definitions/Inventory"},
                        "examples": {
                            "application/json": {
                                "id": 1,
                                "name": "Oil Filter",
                                "price": 12.99,
                            }
                        },
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                },
            },
            "get": {
                "tags": ["Inventory"],
                "summary": "Get all inventory parts",
                "description": "Returns a list of all parts in the inventory.",
                "responses": {
                    "200": {
                        "description": "List of all inventory parts",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/Inventory"},
                        },
                        "examples": {
                            "application/json": [
                                {"id": 1, "name": "Oil Filter", "price": 12.99},
                                {"id": 2, "name": "Brake Pad", "price": 45.00},
                            ]
                        },
                    }
                },
            },
        },
        "/inventory/{id}": {
            "get": {
                "tags": ["Inventory"],
                "summary": "Get an inventory part by ID",
                "description": "Returns a single inventory part by its unique ID.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The inventory part's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Inventory part found",
                        "schema": {"$ref": "#/definitions/Inventory"},
                    },
                    "404": {
                        "description": "Inventory part not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            },
            "put": {
                "tags": ["Inventory"],
                "summary": "Update an inventory part by ID",
                "description": "Updates the name and/or price of an existing inventory part.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The inventory part's unique ID",
                    },
                    {
                        "in": "body",
                        "name": "body",
                        "required": True,
                        "schema": {"$ref": "#/definitions/InventoryInput"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Inventory part updated successfully",
                        "schema": {"$ref": "#/definitions/Inventory"},
                    },
                    "400": {"description": "Validation error", "schema": {"$ref": "#/definitions/Error"}},
                    "404": {
                        "description": "Inventory part not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            },
            "delete": {
                "tags": ["Inventory"],
                "summary": "Delete an inventory part by ID",
                "description": "Permanently removes an inventory part from the system.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "id",
                        "required": True,
                        "type": "integer",
                        "description": "The inventory part's unique ID",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Inventory part deleted successfully",
                        "schema": {"$ref": "#/definitions/Message"},
                        "examples": {
                            "application/json": {
                                "message": "Inventory item 1 deleted successfully"
                            }
                        },
                    },
                    "404": {
                        "description": "Inventory part not found",
                        "schema": {"$ref": "#/definitions/Error"},
                    },
                },
            },
        },
    },
}

# ── Blueprint: serves the raw JSON spec ──────────────────────────────────────
swagger_json_bp = Blueprint("swagger_json", __name__)


@swagger_json_bp.route("/api/swagger.json")
def serve_swagger_json():
    return jsonify(SWAGGER_SPEC)


# ── Blueprint: serves the Swagger UI ─────────────────────────────────────────
swagger_ui_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Mechanic Shop API"},
)
