from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='nome', description='Filtrar por nome', required=False, type=OpenApiTypes.STR,
                             location=OpenApiParameter.QUERY),
        ],
        responses={200: TagSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
