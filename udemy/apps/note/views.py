from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core import mixins
from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.note.models import Note
from udemy.apps.note.serializer import NoteSerializer


class NoteViewSet(
    mixins.RetrieveRelatedObjectMixin,
    mixins.AnnotateIsEnrolledPermissionMixin,
    ModelViewSet
):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsEnrolled, IsCreatorObject]

    class Meta:
        model = Note
