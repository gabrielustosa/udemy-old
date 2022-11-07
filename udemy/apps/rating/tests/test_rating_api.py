from django.test import TestCase
from parameterized import parameterized

from rest_framework import status
from django.shortcuts import reverse
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.utils import create_factory_in_batch
from tests.factories.course import CourseFactory
from tests.factories.rating import RatingFactory
from tests.factories.user import UserFactory
from udemy.apps.course.models import CourseRelation
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer

RATING_LIST_URL = reverse('rating-list')


def rating_detail_url(pk): return reverse('rating-detail', kwargs={'pk': pk})


class PublicRatingAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_rating_list(self):
        ratings = create_factory_in_batch(RatingFactory, 5)

        response = self.client.get(RATING_LIST_URL)

        serializer = RatingSerializer(ratings, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rating_retrieve(self):
        rating = RatingFactory()

        response = self.client.get(rating_detail_url(pk=1))

        serializer = RatingSerializer(rating)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_cant_create_rating(self):
        response = self.client.post(RATING_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRatingApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_rating_create(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cant_rating_course_twice(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        RatingFactory(creator=self.user, course=course)

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cant_rate_a_course_not_enrolled(self):
        course = CourseFactory()

        payload = {
            'course': course.id,
            'rating': 3,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand([
        (0,),
        (6,)
    ])
    def test_user_cant_create_a_rating_with_rate_greater_than_5_less_than_1(self, rating):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

        payload = {
            'course': course.id,
            'rating': rating,
            'comment': 'test',
        }

        response = self.client.post(RATING_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_rating_update(self):
        original_comment = 'original comment'
        rating = RatingFactory(comment=original_comment, creator=self.user)
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)

        payload = {
            'rating': 3,
        }
        response = self.client.patch(rating_detail_url(pk=rating.id), payload)

        rating.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating.rating, payload['rating'])
        self.assertEqual(rating.comment, original_comment)

    def test_rating_full_update(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        rating = RatingFactory(creator=self.user)

        payload = {
            'course': 1,
            'rating': 3,
            'comment': 'new comment',
        }
        response = self.client.put(rating_detail_url(pk=rating.id), payload)

        rating.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(rating.rating, payload['rating'])
        self.assertEqual(rating.comment, payload['comment'])

    def test_delete_rating(self):
        course = CourseFactory()
        CourseRelation.objects.create(course=course, creator=self.user, current_lesson=1)
        rating = RatingFactory(creator=self.user)

        response = self.client.delete(rating_detail_url(pk=rating.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Rating.objects.filter(id=rating.id).exists())