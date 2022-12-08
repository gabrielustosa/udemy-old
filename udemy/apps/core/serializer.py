from rest_framework import serializers

from udemy.apps.core.mixins import serializer


class ModelSerializer(
    serializer.DynamicModelFieldsMixin,
    serializer.RelatedObjectMixin,
    serializer.CreateAndUpdateOnlyFieldsMixin,
    serializer.PermissionForFieldMixin,
    serializer.ExpandedFieldMixin,
    serializers.ModelSerializer
):
    """
    Custom ModelSerializer
    """
