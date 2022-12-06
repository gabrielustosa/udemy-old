from rest_framework import serializers

from udemy.apps.category.serializer import CategorySerializer
from udemy.apps.core.serializer import ModelSerializer
from udemy.apps.core.permissions import IsEnrolled
from udemy.apps.course.models import Course
from udemy.apps.user.serializer import UserSerializer


class CourseSerializer(ModelSerializer):
    num_modules = serializers.SerializerMethodField()
    num_lessons = serializers.SerializerMethodField()
    num_contents = serializers.SerializerMethodField()
    num_contents_info = serializers.SerializerMethodField()
    num_subscribers = serializers.SerializerMethodField()
    estimated_content_length_video = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'headline', 'language', 'description',
            'is_paid', 'price', 'created', 'modified', 'avg_rating',
            'requirements', 'what_you_will_learn', 'num_contents_info',
            'categories', 'instructors', 'num_modules', 'url', 'num_subscribers',
            'num_lessons', 'num_contents', 'estimated_content_length_video'
        ]
        extra_kwargs = {
            'instructors': {'allow_empty': True},
        }
        related_objects = {
            'instructors': {
                'serializer': UserSerializer
            },
            'categories': {
                'serializer': CategorySerializer,
            },
            'quizzes': {
                'serializer': 'udemy.apps.quiz.serializer.QuizSerializer',
                'permissions': [IsEnrolled],
                'filter': {'is_published': True},
            },
            'lessons': {
                'serializer': 'udemy.apps.lesson.serializer.LessonSerializer',
                'permissions': [IsEnrolled]
            },
            'modules': {
                'serializer': 'udemy.apps.module.serializer.ModuleSerializer',
                'permissions': [IsEnrolled]
            },
            'contents': {
                'serializer': 'udemy.apps.content.serializer.ContentSerializer',
                'permissions': [IsEnrolled]
            },
            'ratings': {
                'serializer': 'udemy.apps.rating.serializer.RatingSerializer',
                'permissions': [IsEnrolled]
            },
            'warning_messages': {
                'serializer': 'udemy.apps.message.serializer.MessageSerializer',
                'permissions': [IsEnrolled]
            },
            'questions': {
                'serializer': 'udemy.apps.question.serializer.QuestionSerializer',
                'permissions': [IsEnrolled]
            },
            'notes': {
                'serializer': 'udemy.apps.note.serializer.NoteSerializer',
                'permissions': [IsEnrolled]
            }
        }
        min_fields = ('id', 'title', 'url')
        default_fields = (*min_fields, 'price', 'is_paid', 'instructors')

    def get_num_modules(self, instance):
        return instance.num_modules

    def get_num_lessons(self, instance):
        return instance.num_lessons

    def get_num_contents(self, instance):
        return instance.num_contents

    def get_avg_rating(self, instance):
        return instance.avg_rating

    def get_url(self, instance):
        return f'https://udemy.com/course/{instance.slug}'

    def get_num_subscribers(self, instance):
        return instance.num_subscribers

    def get_num_contents_info(self, instance):
        return {
            'text': instance.content_num_text,
            'link': instance.content_num_link,
            'file': instance.content_num_file,
            'image': instance.content_num_image,
        }

    def get_estimated_content_length_video(self, instance: Course):
        return instance.estimated_content_length_video

    def get_related_objects(self):
        related_objects = super().get_related_objects()
        if self.context.get('request'):
            related_objects['notes']['filter'] = {
                'creator': self.context.get('request').user
            }
        return related_objects

    def create(self, validated_data):
        user = self.context.get('request').user

        course = super().create(validated_data)
        course.instructors.add(user)

        return course
