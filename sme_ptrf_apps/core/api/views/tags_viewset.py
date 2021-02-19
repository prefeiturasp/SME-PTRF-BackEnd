from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from django_filters.rest_framework import DjangoFilterBackend

from ..serializers.tag_serializer import TagSerializer
from ...models import Tag


class TagsViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Tag.objects.all().order_by('nome')
    serializer_class = TagSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        qs = Tag.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs.order_by('nome')

