from random import randint

from django.test import TestCase

from parameterized import parameterized

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.factories.course import CourseFactory
from tests.factories.lesson import LessonFactory
from tests.factories.module import ModuleFactory
from tests.utils import create_factory_in_batch
from tests.factories.user import UserFactory
from udemy.apps.content.serializer import ContentSerializer

from udemy.apps.course.models import CourseRelation
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.lesson.models import Lesson
from udemy.apps.lesson.serializer import LessonSerializer
from udemy.apps.module.serializer import ModuleSerializer
from udemy.apps.quiz.serializer import QuestionSerializer

LESSON_LIST_URL = reverse('lesson-list')


def lesson_detail_url(pk): return reverse('lesson-detail', kwargs={'pk': pk})


class PublicLessonAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_cant_create_lesson(self):
        response = self.client.post(LESSON_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLessonApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_create_lesson(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory(course=course)

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'module': module.id,
            'course': course.id
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        lesson = Lesson.objects.first()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(lesson.title, payload['title'])
        self.assertEqual(lesson.video, payload['video'])

    def test_lesson_retrieve(self):
        lesson = LessonFactory()
        CourseRelation.objects.create(course=lesson.course, creator=self.user)

        response = self.client.get(lesson_detail_url(pk=lesson.id))

        serializer = LessonSerializer(lesson)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_not_enrolled_can_retrieve_lesson(self):
        lesson = LessonFactory()

        response = self.client.get(lesson_detail_url(lesson.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_lesson_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)

        payload = {
            'title': 'new title',
        }
        response = self.client.patch(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_lesson_full_update(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)

        payload = {
            'title': 'new title',
            'video': 'https://www.youtube.com/watch?v=dawjkb_dwadaws',
        }
        response = self.client.put(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.title, payload['title'])

    def test_delete_lesson(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        lesson = LessonFactory(course=course)

        response = self.client.delete(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())

    def test_not_course_instructor_cant_create_a_lesson(self):
        course = CourseFactory()
        module = ModuleFactory(course=course)

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'video_id': 'E6CdIawPTh0',
            'video_duration': 1,
            'module': module.id,
            'course': course.id
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_update_lesson(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)

        user = UserFactory()
        self.client.force_authenticate(user)

        response_patch = self.client.patch(lesson_detail_url(pk=lesson.id))
        response_put = self.client.put(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response_patch.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_instructor_cant_delete_lesson(self):
        course = CourseFactory()
        lesson = LessonFactory(course=course)

        response = self.client.delete(lesson_detail_url(pk=lesson.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_send_a_order_greater_than_max_order_lesson(self):
        course = CourseFactory()
        course.instructors.add(self.user)

        lessons = create_factory_in_batch(LessonFactory, 5, course=course)

        payload = {
            'order': 6,
        }

        response = self.client.patch(lesson_detail_url(pk=lessons[0].id), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @parameterized.expand([
        (3, 6),
        (8, 2),
        (1, 10),
        (9, 2),
        (10, 2),
        (5, 5),
    ])
    def test_lesson_reorder_field(self, current_order, new_order):
        course = CourseFactory()
        module = ModuleFactory(course=course)
        course.instructors.add(self.user)

        create_factory_in_batch(LessonFactory, 10, course=course, module=module)

        lesson = Lesson.objects.filter(order=current_order).first()

        payload = {
            'order': new_order
        }

        response = self.client.patch(lesson_detail_url(pk=lesson.id), payload)

        lesson.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.order, new_order)

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)

    def test_order_lesson_is_generated_correctly(self):
        course = CourseFactory()
        modules = create_factory_in_batch(ModuleFactory, 5, course=course)
        course.instructors.add(self.user)

        create_factory_in_batch(LessonFactory, 25, course=course, module=modules[randint(0, 4)])

        for index, model in enumerate(Lesson.objects.all(), start=1):
            self.assertEqual(model.order, index)

    @parameterized.expand([
        ('module', ('id', 'title'), ModuleSerializer),
        ('course', ('id', 'title'), CourseSerializer),
    ])
    def test_related_objects(self, field_name, fields, Serializer):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        CourseRelation.objects.create(creator=self.user, course=course)

        response = self.client.get(
            f'{lesson_detail_url(lesson.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        lesson_serializer = LessonSerializer(lesson, fields=('@min',))
        object_serializer = Serializer(getattr(lesson, field_name), fields=fields)

        expected_response = {
            **lesson_serializer.data,
            field_name: {
                **object_serializer.data
            }
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @parameterized.expand([
        ('contents', ('id', 'name'), ContentSerializer),
        ('questions', ('id', 'title'), QuestionSerializer),
    ])
    def test_related_objects_m2m(self, field_name, fields, Serializer):
        course = CourseFactory()
        lesson = LessonFactory(course=course)
        CourseRelation.objects.create(creator=self.user, course=course)

        response = self.client.get(
            f'{lesson_detail_url(lesson.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        lesson_serializer = LessonSerializer(lesson, fields=('@min',))
        object_serializer = Serializer(getattr(lesson, field_name).all(), fields=fields, many=True)

        expected_response = {
            **lesson_serializer.data,
            field_name: object_serializer.data
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_response)

    @parameterized.expand([
        ('contents', ('id', 'name')),
        ('questions', ('id', 'title')),
    ])
    def test_related_objects_m2m_permissions(self, field_name, fields):
        course = CourseFactory()
        lesson = LessonFactory(course=course)

        response = self.client.get(
            f'{lesson_detail_url(lesson.id)}?fields[{field_name}]={",".join(fields)}&fields=@min')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_for_field(self):
        course = CourseFactory()
        course.instructors.add(self.user)
        module = ModuleFactory()

        payload = {
            'title': 'string',
            'video': 'https://www.youtube.com/watch?v=Ejkb_YpuHWs',
            'module': module.id,
            'course': course.id
        }
        response = self.client.post(LESSON_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
