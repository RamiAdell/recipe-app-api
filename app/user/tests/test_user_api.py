from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status # noqa
from core import models # noqa


CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
"""helper functions"""


def create_user(**params):
    """create and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """test the public features"""
    def setUp(self):
        self.client = APIClient()

    def test_email_creation(self):
        payload = { # noqa
            'name': 'rami',
            'password': '12225',
            'email': 'rami@mail.com'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))

        self.assertNotIn('password', res)

    def test_check_user_with_email_exists(self):
        payload = { # noqa
            'name': 'rami',
            'password': '123',
            'email': 'rami@mail.com'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creating_with_small_password(self):
        payload = { # noqa
            'name': 'rami',
            'password': '123',
            'email': 'rami@mail.com'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(email=payload['email']).exists()) # noqa

    def test_creating_token(self):
        info = {
            'name': 'rami',
            'password': 'rami123',
            'email': 'h@mail.com',
        }

        payload = {
            'email': info['email'],
            'password': info['password'],
        }

        create_user(**info)
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_bad_cred(self):
        info = {
            'name': 'rami',
            'password': 'rami123',
            'email': 'test@mail.com',
        }
        payload = {
            'email': 'rami',
            'password': 'testsa',
        }
        create_user(**info)
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        payload = {
            'email': 'rami@mail.com',
            'password': '',
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauth_user(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='ramia@mail.com',
            password='ramail.com',
            name='ramiamail.com',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_method(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_method(self):
        payload = {
            'name': 'rami',
            'password': 'rami123',
            'email': 'test@mail.com',
        }

        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))  # asd
        self.assertEqual(res.status_code, status.HTTP_200_OK)
