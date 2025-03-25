""" test for models """
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        email = 'test@emample.com'
        password = 'test@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_emails_capitilizations(self):
        emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@EXAMPLE.COM', 'test4@example.com'],
        ]
        for email, expected in emails:
            user = get_user_model().objects.create_user(email)
            self.assertEqual(user.email, expected)

    def test_non_email_users(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '123456')

    def test_create_super_user(self):
        email = 'test@emample.com'
        password = 'test@123'
        user = get_user_model().objects.create_superuser(email, password)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
