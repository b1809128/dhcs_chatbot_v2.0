import unittest
from importlib.util import find_spec


if find_spec("flask") is not None:
    from app import app
else:
    app = None


@unittest.skipIf(app is None, "Flask is not installed in the current environment")
class AppAuthorizationTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_guest_can_only_access_admission_queries(self):
        response = self.client.post("/chat", json={"message": "lịch học lớp dths3"})

        self.assertEqual(response.status_code, 403)
        payload = response.get_json()
        self.assertIn("đăng nhập", payload["reply"].lower())
        self.assertIn("Chỉ tiêu tuyển sinh", payload["suggestions"])

    def test_guest_can_access_admission_queries(self):
        response = self.client.post("/chat", json={"message": "tuyển sinh"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "TUYỂN SINH")

    def test_guest_can_access_specific_admission_topics(self):
        response = self.client.post("/chat", json={"message": "hồ sơ nhập học"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "HỒ SƠ TUYỂN SINH")

    def test_authenticated_user_can_access_internal_queries(self):
        login_response = self.client.post(
            "/login",
            data={
                "username": app.config["CHATBOT_USERNAME"],
                "password": app.config["CHATBOT_PASSWORD"],
            },
        )

        self.assertEqual(login_response.status_code, 302)

        response = self.client.post("/chat", json={"message": "lịch học lớp dths3"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["reply"], "LỊCH HỌC")


if __name__ == "__main__":
    unittest.main()
