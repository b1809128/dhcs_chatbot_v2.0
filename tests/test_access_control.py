import unittest

from services.chatbot.access_control import is_public_query


class AccessControlTests(unittest.TestCase):
    def test_guest_can_access_general_admission_query(self):
        self.assertTrue(is_public_query("tuyển sinh"))

    def test_guest_can_access_specific_admission_query(self):
        self.assertTrue(is_public_query("hồ sơ nhập học"))
        self.assertTrue(is_public_query("bài thi vb2ca"))
        self.assertTrue(is_public_query("tuyen sinh van bang 2"))

    def test_guest_cannot_access_internal_query(self):
        self.assertFalse(is_public_query("lịch học lớp dths3"))
        self.assertFalse(is_public_query("giờ mở cửa thư viện"))


if __name__ == "__main__":
    unittest.main()
