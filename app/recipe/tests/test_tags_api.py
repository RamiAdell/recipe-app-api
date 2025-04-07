from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Tag, Recipe
from rest_framework.test import APIClient
from rest_framework import status
from recipe.serializers import TagSerializer
from decimal import Decimal


TAGS_URL = reverse('recipe:tag-list')


def detail_url(id):
    return reverse('recipe:tag-detail', args=[id])


def create_user(email='user@example.com', password='testpass123'):
    """create and return new user"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email='test2@example.com')
        Tag.objects.create(user=user2, name='Comfort')
        tag = Tag.objects.create(user=self.user, name='Vegan')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        payload = {'name': 'Desert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='After breakfast')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tag_assigned_to_recipe(self):
        tag1 = Tag.objects.create(user=self.user, name='Apples')
        tag2 = Tag.objects.create(user=self.user, name='Turkey')

        recipe = Recipe.objects.create(
            title='Apple crumble 2',
            time_minutes=5,
            price=Decimal('4.5'),
            user=self.user,
            )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        tag = Tag.objects.create(user=self.user, name='Eggs')
        Tag.objects.create(user=self.user, name='Lentis')

        recipe1 = Recipe.objects.create(
            title='Egg crumble 2',
            time_minutes=50,
            price=Decimal('7.5'),
            user=self.user,
            )
        recipe2 = Recipe.objects.create(
            title='Egg Herb 2',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
            )

        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
