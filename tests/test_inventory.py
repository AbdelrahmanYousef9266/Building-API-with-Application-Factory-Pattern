import unittest
import json
from tests.base import BaseTestCase


class TestInventory(BaseTestCase):
    """Tests for /inventory routes."""

    # ── Helpers ──────────────────────────────────────────────────────────────

    def create_inventory(self, name="Oil Filter", price=12.99):
        """Creates an inventory part and returns the response."""
        return self.client.post("/inventory/", json={
            "name": name,
            "price": price,
        })

    # ── Positive Tests ────────────────────────────────────────────────────────

    def test_create_inventory_success(self):
        """POST /inventory/ with valid data returns 201 and the new part."""
        response = self.create_inventory()
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Oil Filter")
        self.assertEqual(data["price"], 12.99)
        self.assertIn("id", data)

    def test_get_all_inventory_success(self):
        """GET /inventory/ returns 200 and a list of all parts."""
        self.create_inventory("Oil Filter", 12.99)
        self.create_inventory("Brake Pad", 45.00)
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_get_inventory_by_id_success(self):
        """GET /inventory/<id> returns 200 and the correct part."""
        self.create_inventory()
        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["name"], "Oil Filter")

    def test_update_inventory_success(self):
        """PUT /inventory/<id> with valid data returns 200 and the updated part."""
        self.create_inventory()
        response = self.client.put("/inventory/1", json={
            "name": "Premium Oil Filter",
            "price": 19.99,
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Premium Oil Filter")
        self.assertEqual(data["price"], 19.99)

    def test_delete_inventory_success(self):
        """DELETE /inventory/<id> returns 200 and the part is gone."""
        self.create_inventory()
        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        # Confirm the part is actually deleted
        get_response = self.client.get("/inventory/1")
        self.assertEqual(get_response.status_code, 404)

    def test_get_all_inventory_empty(self):
        """GET /inventory/ with no parts returns 200 and an empty list."""
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_create_multiple_inventory_items(self):
        """Creating multiple inventory parts assigns unique IDs."""
        self.create_inventory("Oil Filter", 12.99)
        self.create_inventory("Brake Pad", 45.00)
        self.create_inventory("Air Filter", 8.50)
        response = self.client.get("/inventory/")
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        ids = [item["id"] for item in data]
        self.assertEqual(len(set(ids)), 3)  # all unique

    # ── Negative Tests ────────────────────────────────────────────────────────

    def test_create_inventory_missing_name(self):
        """POST /inventory/ without a name returns 400."""
        response = self.client.post("/inventory/", json={"price": 12.99})
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_missing_price(self):
        """POST /inventory/ without a price returns 400."""
        response = self.client.post("/inventory/", json={"name": "Oil Filter"})
        self.assertEqual(response.status_code, 400)

    def test_create_inventory_empty_body(self):
        """POST /inventory/ with empty body returns 400."""
        response = self.client.post("/inventory/", json={})
        self.assertEqual(response.status_code, 400)

    def test_get_inventory_invalid_id(self):
        """GET /inventory/9999 returns 404 when the part does not exist."""
        response = self.client.get("/inventory/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_inventory_invalid_id(self):
        """PUT /inventory/9999 returns 404 when the part does not exist."""
        response = self.client.put("/inventory/9999", json={
            "name": "Ghost Part",
            "price": 0.00,
        })
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_delete_inventory_invalid_id(self):
        """DELETE /inventory/9999 returns 404 when the part does not exist."""
        response = self.client.delete("/inventory/9999")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_inventory_missing_fields(self):
        """PUT /inventory/<id> with missing required fields returns 400."""
        self.create_inventory()
        response = self.client.put("/inventory/1", json={"name": "Only Name"})
        self.assertEqual(response.status_code, 400)

    def test_update_inventory_empty_body(self):
        """PUT /inventory/<id> with empty body returns 400."""
        self.create_inventory()
        response = self.client.put("/inventory/1", json={})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
