from django.test import TestCase # noqa
from django.contrib.auth import get_user_model # noqa
from django.urls import reverse # noqa
from core.models import Recipe, Tag # noqa
from rest_framework.test import APIClient # noqa
from rest_framework import status # noqa
from core.models import Ingredient, Recipe# noqa
from decimal import Decimal # noqa
from recipe.serializers import IngredientSerializer # noqa

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(id):
    return reverse('recipe:ingredient-detail', args=[id])


def create_user(email='user@example.com', password='testpass123'):
    """create and return new user"""
    return get_user_model().objects.create_user(email, password)


class PublicIngredientsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serialzier = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialzier.data)

    def test_ingredients_limited_to_user(self):
        user2 = create_user(email="ramyadel@mail.com")
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_updade_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        payload = {'name': 'Coriander'}

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='trameasu')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredient_assigned_to_recipes(self):
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=Decimal('4.5'),
            user=self.user,
            )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentis')

        recipe1 = Recipe.objects.create(
            title='Egg crumble',
            time_minutes=50,
            price=Decimal('7.5'),
            user=self.user,
            )
        recipe2 = Recipe.objects.create(
            title='Egg Herb',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
            )

        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
