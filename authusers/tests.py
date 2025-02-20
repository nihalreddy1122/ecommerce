from django.test import TestCase
from django.utils.timezone import now, timedelta
from authusers.models import TemporaryUser
from authusers.tasks import delete_expired_temp_users

class TestCeleryTasks(TestCase):
    def setUp(self):
        # Create an expired TemporaryUser
        TemporaryUser.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            user_type="customer",
            password="hashed_password",
            otp="123456",
            created_at=now() - timedelta(minutes=10),
        )

    def test_delete_expired_temp_users(self):
        # Run the task
        delete_expired_temp_users()

        # Assert that the TemporaryUser has been deleted
        self.assertEqual(TemporaryUser.objects.count(), 0)
