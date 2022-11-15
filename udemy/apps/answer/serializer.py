from rest_framework import serializers

from udemy.apps.answer.models import Answer
from udemy.apps.core.fields import GenericField, ModelSerializer
from udemy.apps.course.serializer import CourseSerializer
from udemy.apps.question.models import Question
from udemy.apps.question.serializer import QuestionSerializer
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer
from udemy.apps.user.serializer import UserSerializer


class AnswerSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    content_object = GenericField({
        Rating: RatingSerializer(),
        Question: QuestionSerializer()
    }, required=False)

    class Meta:
        model = Answer
        fields = [
            'id', 'creator', 'content',
            'created', 'modified', 'course',
            'likes_count', 'dislikes_count',
            'content_object',
        ]
        related_objects = {
            'creator': UserSerializer,
            'course': CourseSerializer
        }

    def get_likes_count(self, instance):
        return instance.actions.filter(action=1).count()

    def get_dislikes_count(self, instance):
        return instance.actions.filter(action=2).count()

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Title must be greater than 5 characters')
        return value

    def validate_content(self, value):
        if len(value) > 999:
            raise serializers.ValidationError('Content must be less than 999 characters')
        return value

    def create(self, validated_data):
        Model = self.context.get('model')
        object_id = self.context.get('object_id')
        validated_data['content_object'] = Model.objects.get(id=object_id)
        return super().create(validated_data)