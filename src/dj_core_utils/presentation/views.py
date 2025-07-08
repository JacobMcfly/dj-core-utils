from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType

from dj_core_utils.presentation.serializers import ContentTypeSerializer, UserSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_content_type(request, app_label=None, model=None):
    obj = get_object_or_404(ContentType, app_label=app_label, model=model)
    return Response(ContentTypeSerializer(obj).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_data(request):
    return Response(UserSerializer(request.user).data)
