import unittest
import json
from tests.base import BaseTestCase


class TestServiceTickets(BaseTestCase):
    """Tests for /service-tickets routes."""

    # ── Helpers ──────────────────────────────────────────────────────────────

    def create_customer(self):
        """Creates a test customer and returns the response."""
        return self.client.post("/customers/", json={
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "555-1234",
            "address": "123 Main St",
            "password": "mypassword123",
        })

    def create_mechanic(self, email="jane@shop.com"):
        """Creates a test mechanic and returns the response."""
        return self.client.post("/mechanics/", json={
            "name": "Jane Doe",
            "email": email,
            "phone": "555-5678",
            "address": "456 Garage Ave",
            "salary": 55000.00,
        })

    def create_inventory(self):
        """Creates a test inventory part and returns the response."""
        return self.client.post("/inventory/", json={
            "name": "Oil Filter",
            "price": 12.99,
        })

    def create_ticket(self, customer_id=1):
        """Creates a service ticket for the given customer ID."""
        return self.client.post("/service-tickets/", json={
            "vin": "1HGBH41JXMN109186",
            "service_description": "Oil change and tire rotation",
            "status": "open",
            "customer_id": customer_id,
        })

    def setUp(self):
        """Set up: create a customer, mechanic, and inventory part for each test."""
        super().setUp()
        self.create_customer()
        self.create_mechanic()
        self.create_inventory()

    # ── Positive Tests ────────────────────────────────────────────────────────

    def test_create_service_ticket_success(self):
        """POST /service-tickets/ with valid data returns 201 and the new ticket."""
        response = self.create_ticket(customer_id=1)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["vin"], "1HGBH41JXMN109186")
        self.assertEqual(data["customer_id"], 1)
        self.assertEqual(data["status"], "open")
        self.assertIn("mechanic_ids", data)
        self.assertIn("inventory_part_ids", data)

    def test_get_all_service_tickets_success(self):
        """GET /service-tickets/ returns 200 and a list of all tickets."""
        self.create_ticket()
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_assign_mechanic_success(self):
        """PUT /service-tickets/<id>/assign-mechanic/<id> returns 200."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/assign-mechanic/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        # Confirm the mechanic appears on the ticket
        ticket_response = self.client.get("/service-tickets/")
        ticket_data = json.loads(ticket_response.data)
        self.assertIn(1, ticket_data[0]["mechanic_ids"])

    def test_remove_mechanic_success(self):
        """PUT /service-tickets/<id>/remove-mechanic/<id> returns 200 after assigning."""
        self.create_ticket()
        # First assign the mechanic
        self.client.put("/service-tickets/1/assign-mechanic/1")
        # Now remove
        response = self.client.put("/service-tickets/1/remove-mechanic/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)

    def test_edit_mechanic_assignments_success(self):
        """PUT /service-tickets/<id>/edit with add_ids returns 200 and updated ticket."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/edit", json={
            "add_ids": [1],
            "remove_ids": [],
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(1, data["mechanic_ids"])

    def test_edit_mechanic_remove_success(self):
        """PUT /service-tickets/<id>/edit with remove_ids removes the mechanic."""
        self.create_ticket()
        self.client.put("/service-tickets/1/assign-mechanic/1")
        response = self.client.put("/service-tickets/1/edit", json={
            "add_ids": [],
            "remove_ids": [1],
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertNotIn(1, data["mechanic_ids"])

    def test_add_part_to_ticket_success(self):
        """PUT /service-tickets/<id>/add-part/<id> returns 200 and the updated ticket."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/add-part/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn(1, data["inventory_part_ids"])

    def test_get_all_tickets_empty(self):
        """GET /service-tickets/ with no tickets returns 200 and an empty list."""
        response = self.client.get("/service-tickets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    def test_assign_mechanic_already_assigned(self):
        """Assigning the same mechanic twice returns 200 (idempotent)."""
        self.create_ticket()
        self.client.put("/service-tickets/1/assign-mechanic/1")
        response = self.client.put("/service-tickets/1/assign-mechanic/1")
        self.assertEqual(response.status_code, 200)

    def test_add_part_already_added(self):
        """Adding the same part twice returns 200 (idempotent)."""
        self.create_ticket()
        self.client.put("/service-tickets/1/add-part/1")
        response = self.client.put("/service-tickets/1/add-part/1")
        self.assertEqual(response.status_code, 200)

    # ── Negative Tests ────────────────────────────────────────────────────────

    def test_create_service_ticket_missing_fields(self):
        """POST /service-tickets/ with missing required fields returns 400."""
        response = self.client.post("/service-tickets/", json={"vin": "1HGBH41JXMN109186"})
        self.assertEqual(response.status_code, 400)

    def test_create_service_ticket_empty_body(self):
        """POST /service-tickets/ with empty body returns 400."""
        response = self.client.post("/service-tickets/", json={})
        self.assertEqual(response.status_code, 400)

    def test_assign_mechanic_invalid_ticket(self):
        """PUT /service-tickets/9999/assign-mechanic/1 returns 404 for missing ticket."""
        response = self.client.put("/service-tickets/9999/assign-mechanic/1")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_assign_mechanic_invalid_mechanic(self):
        """PUT /service-tickets/1/assign-mechanic/9999 returns 404 for missing mechanic."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/assign-mechanic/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_remove_mechanic_not_assigned(self):
        """Removing a mechanic that is not assigned returns 400."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/remove-mechanic/1")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_remove_mechanic_invalid_ticket(self):
        """PUT /service-tickets/9999/remove-mechanic/1 returns 404 for missing ticket."""
        response = self.client.put("/service-tickets/9999/remove-mechanic/1")
        self.assertEqual(response.status_code, 404)

    def test_remove_mechanic_invalid_mechanic(self):
        """PUT /service-tickets/1/remove-mechanic/9999 returns 404 for missing mechanic."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/remove-mechanic/9999")
        self.assertEqual(response.status_code, 404)

    def test_edit_invalid_service_ticket_id(self):
        """PUT /service-tickets/9999/edit returns 404 for missing ticket."""
        response = self.client.put("/service-tickets/9999/edit", json={
            "add_ids": [1],
            "remove_ids": [],
        })
        self.assertEqual(response.status_code, 404)

    def test_add_part_invalid_ticket(self):
        """PUT /service-tickets/9999/add-part/1 returns 404 for missing ticket."""
        response = self.client.put("/service-tickets/9999/add-part/1")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_add_part_invalid_inventory(self):
        """PUT /service-tickets/1/add-part/9999 returns 404 for missing inventory part."""
        self.create_ticket()
        response = self.client.put("/service-tickets/1/add-part/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
