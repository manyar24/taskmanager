import os
import tempfile
import unittest

from app import create_app


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.app = create_app({"DATABASE_URL": f"sqlite:///{self.tmp.name}", "TESTING": True, "JWT_SECRET_KEY": "test-secret"})
        self.client = self.app.test_client()
        self.token = self.register_and_login()

    def tearDown(self):
        try:
            os.remove(self.tmp.name)
        except FileNotFoundError:
            pass

    def auth(self):
        return {"Authorization": f"Bearer {self.token}"}

    def register_and_login(self):
        r = self.client.post("/api/v1/auth/register", json={"name": "Test User", "email": "test@example.com", "password": "StrongPass123"})
        self.assertEqual(r.status_code, 201)
        return r.get_json()["data"]["access_token"]

    def make(self, **kwargs):
        body = {"title": "Write report", **kwargs}
        return self.client.post("/api/v1/tasks", json=body, headers=self.auth())

    def test_authentication(self):
        self.assertEqual(self.client.get("/api/v1/tasks").status_code, 401)
        r = self.client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "wrongpass"})
        self.assertEqual(r.status_code, 401)
        r = self.client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "StrongPass123"})
        self.assertEqual(r.status_code, 200)

    def test_create_and_retrieve(self):
        r = self.make(description="Q3", priority="high", due_date="2026-12-01")
        self.assertEqual(r.status_code, 201)
        task = r.get_json()["data"]
        self.assertEqual(task["status"], "todo")
        got = self.client.get(f"/api/v1/tasks/{task['id']}", headers=self.auth())
        self.assertEqual(got.status_code, 200)
        self.assertEqual(got.get_json()["data"], task)

    def test_validation(self):
        self.assertEqual(self.client.post("/api/v1/tasks", json={}, headers=self.auth()).status_code, 422)
        self.assertEqual(self.make(status="nope").status_code, 422)
        self.assertEqual(self.make(due_date="2026-02-30").status_code, 422)
        self.assertEqual(self.make(title="   ").status_code, 422)
        self.assertEqual(self.make(bogus=1).status_code, 422)

    def test_crud_search_filter_pagination(self):
        self.make(title="Buy milk", priority="low")
        self.make(title="Buy 100% cotton", status="done", priority="high")
        self.make(title="Write code", priority="high")
        r = self.client.get("/api/v1/tasks?q=buy", headers=self.auth())
        self.assertEqual([x["title"] for x in r.get_json()["data"]], ["Buy milk", "Buy 100% cotton"])
        r = self.client.get("/api/v1/tasks?priority=high&status=done", headers=self.auth())
        self.assertEqual(len(r.get_json()["data"]), 1)
        tid = self.make(description="d", priority="low").get_json()["data"]["id"]
        p = self.client.patch(f"/api/v1/tasks/{tid}", json={"status": "done"}, headers=self.auth())
        self.assertEqual(p.status_code, 200)
        self.assertEqual(p.get_json()["data"]["status"], "done")
        u = self.client.put(f"/api/v1/tasks/{tid}", json={"title": "New"}, headers=self.auth())
        self.assertEqual(u.status_code, 200)
        self.assertIsNone(u.get_json()["data"]["description"])
        self.assertEqual(self.client.delete(f"/api/v1/tasks/{tid}", headers=self.auth()).status_code, 204)
        self.assertEqual(self.client.get(f"/api/v1/tasks/{tid}", headers=self.auth()).status_code, 404)

    def test_user_isolation(self):
        task = self.make().get_json()["data"]
        self.client.post("/api/v1/auth/register", json={"name": "Other", "email": "other@example.com", "password": "StrongPass123"})
        login = self.client.post("/api/v1/auth/login", json={"email": "other@example.com", "password": "StrongPass123"})
        other = login.get_json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {other}"}
        self.assertEqual(self.client.get(f"/api/v1/tasks/{task['id']}", headers=headers).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/v1/tasks/{task['id']}", headers=headers).status_code, 404)

    def test_health_and_openapi(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/openapi.json").status_code, 200)
        self.assertEqual(self.client.get("/api/docs").status_code, 200)


if __name__ == "__main__":
    unittest.main()
