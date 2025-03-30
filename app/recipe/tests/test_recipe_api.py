"""Test for recipe API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Recipe
from rest_framework.test import APIClient
from rest_framework import status # noqa
from core import models # noqa
from decimal import Decimal
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer # noqa

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        'title': 'Sample Title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample Title',
        'link': 'http://example.com/recipe.pdf',
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='6465452')
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_for_user(self):
        another_user = create_user(email='user2@example.com', password='6465452')  # noqa

        create_recipe(user=self.user)
        create_recipe(user=another_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        payload = {
            'title': 'Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)  # recipe.key
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):

        original_link = 'http://example.com'
        recipe = create_recipe(
            user=self.user,
            title='sample',
            link=original_link,
        )

        payload = {'title': 'New Recipe title'}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_full_update(self):
        recipe = create_recipe(
            user=self.user,
            title='sample',
            link='http://example.com',
        )
        payload = {
            'title': 'Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            'link': 'http://newexample.com',
            }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)  # recipe.key
        self.assertEqual(recipe.user, self.user)
