from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from udemy.apps.action.models import Action
from udemy.apps.answer.models import Answer
from udemy.apps.core.models import TimeStampedBase, CreatorBase
from udemy.apps.course.models import Course
from udemy.apps.lesson.models import Lesson


class Question(CreatorBase, TimeStampedBase):
    lesson = models.ForeignKey(
        Lesson,
        related_name='questions',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name='questions',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    actions = GenericRelation(Action)
    answers = GenericRelation(Answer)

    def __str__(self):
        return self.title


