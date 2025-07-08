from rest_framework.response import Response
from rest_framework import status


class UniversalStateQuerysetMixin:
    """
    Filter the queryset by universal_state='active' if the model has it.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(queryset.model, 'universal_state'):
            return queryset.filter(universal_state='active')
        return queryset


class UniversalStateSoftDeleteMixin:
    """
    Replaces soft-delete deletion logic using universal_state.
    Compatible with perform_destroy().
    """
    def perform_destroy(self, instance):
        if hasattr(instance, 'universal_state'):
            instance.universal_state = 'terminated'
            instance.save()
        else:
            super().perform_destroy(instance)


class UniversalStateDestroyMixin:
    """
    Alternative to use if you prefer to override destroy directly.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'universal_state'):
            instance.universal_state = 'terminated'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)


class ActionSerializerMixin:
    """
    Mixin that allows using different serializers per action, including standard and custom actions.

    Define a single dictionary:
        action_serializer_classes = {
            'list': ListSerializer,
            'retrieve': RetrieveSerializer,
            'create': CreateSerializer,
            'update': UpdateSerializer,
            'partial_update': PartialUpdateSerializer,
            'my_custom_action': MyCustomSerializer,
        }
    """
    action_serializer_classes = {}

    def get_serializer_class(self):
        action = getattr(self, 'action', None)
        if action in self.action_serializer_classes:
            return self.action_serializer_classes[action]
        return super().get_serializer_class()
