import unittest
import json
from tests.base import BaseTestCase


class TestCustomers(BaseTestCase):
    """Tests for /customers routes."""

    # ── Helpers ──────────────────────────────────────────────────────────────

    def create_customer(self, email="john@example.com", name="John Smith"):
        """Creates a customer and returns the response."""
        return self.client.post("/customers/", json={
            "name": name,
            "email": email,
            "phone": "555-1234",
            "address": "123 Main St",
            "password": "mypassword123",
        })

    def login(self, email="john@example.com", password="mypassword123"):
        """Logs in and returns the JWT token string."""
        response = self.client.post("/customers/login", json={
            "email": email,
            "password": password,
        })
        return json.loads(response.data)["token"]

    # ── Positive Tests ────────────────────────────────────────────────────────

    def test_create_customer_success(self):
        """POST /customers/ with valid data returns 201 and the new customer."""
        response = self.create_customer()
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "John Smith")
        self.assertEqual(data["email"], "john@example.com")
        # Password must never appear in the response
        self.assertNotIn("password", data)

    def test_get_all_customers_success(self):
        """GET /customers/ returns 200 with a paginated response."""
        self.create_customer()
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("customers", data)
        self.assertIn("page", data)
        self.assertIn("total", data)
        self.assertEqual(len(data["customers"]), 1)

    def test_get_customer_by_id_success(self):
        """GET /customers/<id> returns 200 and the correct customer."""
        self.create_customer()
        response = self.client.get("/customers/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["email"], "john@example.com")

    def test_update_customer_success(self):
        """PUT /customers/<id> with valid data returns 200 and updated customer."""
        self.create_customer()
        response = self.client.put("/customers/1", json={
            "name": "John Updated",
            "email": "updated@example.com",
            "phone": "555-9999",
            "address": "999 New Ave",
            "password": "newpassword",
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "John Updated")
        self.assertEqual(data["email"], "updated@example.com")

    def test_delete_customer_success(self):
        """DELETE /customers/<id> returns 200 and the customer is gone."""
        self.create_customer()
        response = self.client.delete("/customers/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        # Confirm the customer is actually deleted
        get_response = self.client.get("/customers/1")
        self.assertEqual(get_response.status_code, 404)

    def test_login_success(self):
        """POST /customers/login with correct credentials returns 200 and a token."""
        self.create_customer()
        response = self.client.post("/customers/login", json={
            "email": "john@example.com",
            "password": "mypassword123",
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("token", data)
        self.assertEqual(data["message"], "Login successful")

    def test_my_tickets_success(self):
        """GET /customers/my-tickets with a valid token returns 200."""
        self.create_customer()
        token = self.login()
        response = self.client.get(
            "/customers/my-tickets",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        # The customer has no tickets yet — should return an empty list
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_pagination_params(self):
        """GET /customers/?page=1&per_page=2 respects pagination params."""
        self.create_customer("a@example.com", "Alice")
        self.create_customer("b@example.com", "Bob")
        self.create_customer("c@example.com", "Carol")
        response = self.client.get("/customers/?page=1&per_page=2")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data["customers"]), 2)
        self.assertEqual(data["per_page"], 2)
        self.assertEqual(data["total"], 3)

    # ── Negative Tests ────────────────────────────────────────────────────────

    def test_create_customer_missing_fields(self):
        """POST /customers/ with missing fields returns 400."""
        response = self.client.post("/customers/", json={"name": "No Email"})
        self.assertEqual(response.status_code, 400)

    def test_create_customer_empty_body(self):
        """POST /customers/ with no body returns 400."""
        response = self.client.post("/customers/", json={})
        self.assertEqual(response.status_code, 400)

    def test_get_customer_invalid_id(self):
        """GET /customers/9999 returns 404 when the customer does not exist."""
        response = self.client.get("/customers/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_customer_invalid_id(self):
        """PUT /customers/9999 returns 404 when the customer does not exist."""
        response = self.client.put("/customers/9999", json={
            "name": "Ghost",
            "email": "ghost@example.com",
            "phone": "000-0000",
            "address": "Nowhere",
            "password": "pass",
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_customer_invalid_id(self):
        """DELETE /customers/9999 returns 404 when the customer does not exist."""
        response = self.client.delete("/customers/9999")
        self.assertEqual(response.status_code, 404)

    def test_login_wrong_password(self):
        """POST /customers/login with wrong password returns 401."""
        self.create_customer()
        response = self.client.post("/customers/login", json={
            "email": "john@example.com",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_login_nonexistent_email(self):
        """POST /customers/login with an email that doesn't exist returns 401."""
        response = self.client.post("/customers/login", json={
            "email": "nobody@example.com",
            "password": "anypassword",
        })
        self.assertEqual(response.status_code, 401)

    def test_login_missing_fields(self):
        """POST /customers/login with missing fields returns 400."""
        response = self.client.post("/customers/login", json={"email": "john@example.com"})
        self.assertEqual(response.status_code, 400)

    def test_my_tickets_missing_token(self):
        """GET /customers/my-tickets without Authorization header returns 401."""
        response = self.client.get("/customers/my-tickets")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_my_tickets_invalid_token(self):
        """GET /customers/my-tickets with a bad token returns 401."""
        response = self.client.get(
            "/customers/my-tickets",
            headers={"Authorization": "Bearer this.is.not.a.valid.token"},
        )
        self.assertEqual(response.status_code, 401)

    def test_my_tickets_malformed_header(self):
        """GET /customers/my-tickets with Authorization not starting with 'Bearer' returns 401."""
        response = self.client.get(
            "/customers/my-tickets",
            headers={"Authorization": "Token sometoken"},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
