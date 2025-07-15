from rest_framework.response import Response
from rest_framework.request import Request
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
            'my_custom_action': {
                'post': MyCustomSerializer,
                'get': MyCustomSerializer
             },
        }
    """
    action_serializer_classes = {}

    def get_serializer_class(self):
        # Get the current action (e.g., 'list', 'retrieve', 'my_user')
        action = getattr(self, 'action', None)

        if action in self.action_serializer_classes:
            serializer_mapping = self.action_serializer_classes[action]

            # Check if the mapping for this action is a dictionary (for per-method serializers)
            if isinstance(serializer_mapping, dict):
                # Ensure self.request exists and has a method
                if hasattr(self, 'request') and isinstance(self.request, Request):
                    http_method = self.request.method.lower()
                    # Return the serializer for the specific HTTP method,
                    # or fallback to the general serializer_class if not found
                    return serializer_mapping.get(http_method, super().get_serializer_class())
                else:
                    # Fallback if request is not available (e.g., during initialization)
                    # Or you can raise an error if this state is unexpected.
                    # For safety, let's fall back to the default
                    return super().get_serializer_class()
            else:
                # If it's not a dictionary, it's a direct serializer class
                return serializer_mapping

        # If the action is not in action_serializer_classes, fall back to the default
        # serializer_class defined in the ViewSet (or what super().get_serializer_class() provides)
        return super().get_serializer_class()
