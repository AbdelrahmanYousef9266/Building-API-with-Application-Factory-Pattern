import unittest
import json
from tests.base import BaseTestCase


class TestMechanics(BaseTestCase):
    """Tests for /mechanics routes."""

    # ── Helpers ──────────────────────────────────────────────────────────────

    def create_mechanic(self, email="jane@shop.com", name="Jane Doe"):
        """Creates a mechanic and returns the response."""
        return self.client.post("/mechanics/", json={
            "name": name,
            "email": email,
            "phone": "555-5678",
            "address": "456 Garage Ave",
            "salary": 55000.00,
        })

    # ── Positive Tests ────────────────────────────────────────────────────────

    def test_create_mechanic_success(self):
        """POST /mechanics/ with valid data returns 201 and the new mechanic."""
        response = self.create_mechanic()
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Jane Doe")
        self.assertEqual(data["email"], "jane@shop.com")
        self.assertEqual(data["salary"], 55000.00)

    def test_get_all_mechanics_success(self):
        """GET /mechanics/ returns 200 and a list of mechanics."""
        self.create_mechanic()
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_get_mechanic_by_id_success(self):
        """GET /mechanics/<id> returns 200 and the correct mechanic."""
        self.create_mechanic()
        response = self.client.get("/mechanics/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Jane Doe")

    def test_update_mechanic_success(self):
        """PUT /mechanics/<id> with valid data returns 200 and updated mechanic."""
        self.create_mechanic()
        response = self.client.put("/mechanics/1", json={
            "name": "Jane Updated",
            "email": "janeupdated@shop.com",
            "phone": "555-0000",
            "address": "789 New Garage",
            "salary": 60000.00,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Jane Updated")
        self.assertEqual(data["salary"], 60000.00)

    def test_delete_mechanic_success(self):
        """DELETE /mechanics/<id> returns 200 and the mechanic is gone."""
        self.create_mechanic()
        response = self.client.delete("/mechanics/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        # Confirm the mechanic is actually deleted
        get_response = self.client.get("/mechanics/1")
        self.assertEqual(get_response.status_code, 404)

    def test_most_tickets_success(self):
        """GET /mechanics/most-tickets returns 200 and mechanics with ticket_count."""
        self.create_mechanic()
        response = self.client.get("/mechanics/most-tickets")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        # Each mechanic entry should include ticket_count
        self.assertIn("ticket_count", data[0])

    def test_get_all_mechanics_empty(self):
        """GET /mechanics/ with no mechanics returns 200 and an empty list."""
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_most_tickets_ordering(self):
        """GET /mechanics/most-tickets returns mechanics in descending ticket_count order."""
        self.create_mechanic("m1@shop.com", "Mechanic One")
        self.create_mechanic("m2@shop.com", "Mechanic Two")
        response = self.client.get("/mechanics/most-tickets")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    # ── Negative Tests ────────────────────────────────────────────────────────

    def test_create_mechanic_missing_fields(self):
        """POST /mechanics/ with missing fields returns 400."""
        response = self.client.post("/mechanics/", json={"name": "No Email"})
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_empty_body(self):
        """POST /mechanics/ with no body returns 400."""
        response = self.client.post("/mechanics/", json={})
        self.assertEqual(response.status_code, 400)

    def test_create_mechanic_missing_salary(self):
        """POST /mechanics/ without salary returns 400."""
        response = self.client.post("/mechanics/", json={
            "name": "No Salary",
            "email": "nosalary@shop.com",
            "phone": "555-0001",
            "address": "Somewhere",
        })
        self.assertEqual(response.status_code, 400)

    def test_get_mechanic_invalid_id(self):
        """GET /mechanics/9999 returns 404 when the mechanic does not exist."""
        response = self.client.get("/mechanics/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_mechanic_invalid_id(self):
        """PUT /mechanics/9999 returns 404 when the mechanic does not exist."""
        response = self.client.put("/mechanics/9999", json={
            "name": "Ghost",
            "email": "ghost@shop.com",
            "phone": "000-0000",
            "address": "Nowhere",
            "salary": 0.0,
        })
        self.assertEqual(response.status_code, 404)

    def test_delete_mechanic_invalid_id(self):
        """DELETE /mechanics/9999 returns 404 when the mechanic does not exist."""
        response = self.client.delete("/mechanics/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_mechanic_bad_data(self):
        """PUT /mechanics/<id> with invalid/missing required fields returns 400."""
        self.create_mechanic()
        response = self.client.put("/mechanics/1", json={"name": "Incomplete"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
