from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.permissions import IsEnrolled, IsCreatorObject
from udemy.apps.note.models import Note
from udemy.apps.note.serializer import NoteSerializer


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsEnrolled, IsCreatorObject]
