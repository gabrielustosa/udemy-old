from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from udemy.apps.core.mixins import RetrieveRelatedObjectMixin, ActionPermissionMixin
from udemy.apps.core.permissions import IsCreatorObject, IsEnrolled
from udemy.apps.rating.models import Rating
from udemy.apps.rating.serializer import RatingSerializer


class RatingViewSet(ActionPermissionMixin, RetrieveRelatedObjectMixin, ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes_by_action = {
        ('default',): [IsAuthenticated, IsCreatorObject, IsEnrolled],
        ('retrieve', 'list'): [AllowAny],
    }

    class Meta:
        model = Rating
