""" test for models """
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from decimal import Decimal
from unittest.mock import patch


def create_user(email='user@example.com', password='testpass123'):
    """create and return new user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            'testtest@mail.com',
            '51648626'
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='sample title',
            time_minutes=5,
            price=Decimal("5.50"),
            description='asd'
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='ingredient1'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
