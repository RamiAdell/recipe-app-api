"""Test for recipe API"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Recipe, Tag, Ingredient # noqa
from rest_framework.test import APIClient
from rest_framework import status # noqa
from core import models # noqa
from decimal import Decimal
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer # noqa
from PIL import Image
import os
import tempfile
RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_recipe_with_tags(self):
        payload = {
            'title': 'Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
            }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        indian_tag = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Not Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            'link': 'http://newexample.com',
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
            }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(indian_tag, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name': 'Lunch'}]
            }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

        payload = {
            'tags': [{'name': 'Lunch'}]
            }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='Desert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {
            'tags': []
            }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_recipe_with_new_ingredients(self):
        payload = {
            'title': 'Not Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            'link': 'http://newexample.com',
            'ingredients': [{'name': 'Indian'}, {'name': 'Breakfast'}]}
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        indian_tag = Ingredient.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Not Sample Title',
            'time_minutes': 30,
            'price': Decimal('5.25'),
            'link': 'http://newexample.com',
            'ingredients': [{'name': 'Indian'}, {'name': 'Breakfast'}]
            }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(indian_tag, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_updating_recipe_with_ingredients(self):

        recipe = create_recipe(user=self.user)
        payload = {
            'ingredients': [{'name': 'Limes'}]
            }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ing = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ing, recipe.ingredients.all())

    def test_update_recipe_assign_ingredients(self):
        ingredient_salt = Ingredient.objects.create(user=self.user, name='Salt') # noqa
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_salt)

        ingredient_sugar = Ingredient.objects.create(user=self.user, name='Sugar') # noqa

        payload = {
            'ingredients': [{'name': 'Sugar'}]
            }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_sugar, recipe.ingredients.all())
        self.assertNotIn(ingredient_salt, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        ingredient_salt = Ingredient.objects.create(user=self.user, name='Salt') # noqa
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_salt)

        payload = {
            'ingredients': []
            }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        r1 = create_recipe(user=self.user, title='Thia')
        r2 = create_recipe(user=self.user, title='tahini')

        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Vegeterian')

        r1.tags.add(tag1)
        r2.tags.add(tag2)

        r3 = create_recipe(user=self.user, title='Fish')

        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        r1 = create_recipe(user=self.user, title='Posh Beans')
        r2 = create_recipe(user=self.user, title='Chicken Cacciatore')

        in1 = Ingredient.objects.create(user=self.user, name='Feta cheese')
        in2 = Ingredient.objects.create(user=self.user, name='Chicken')

        r1.ingredients.add(in1)
        r2.ingredients.add(in2)

        r3 = create_recipe(user=self.user, title='Red Lentil')

        params = {'ingredients': f'{in1.id},{in2.id}'}

        res = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='6465452')
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_uploading_imag_bad_request(self):
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'noimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
