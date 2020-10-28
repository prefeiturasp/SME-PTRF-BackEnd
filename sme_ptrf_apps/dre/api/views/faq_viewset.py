from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..serializers.faq_serializer import FaqSerializer
from ...models import Faq


class FaqsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('categoria__uuid', )
