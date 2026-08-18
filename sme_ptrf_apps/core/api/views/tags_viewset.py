from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.core.models.recurso import Recurso

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
        recurso_uuid = self.request.query_params.get('recurso_uuid')

        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        if recurso_uuid is not None:
            recurso = Recurso.objects.filter(uuid=recurso_uuid).first()
            if recurso:
                qs = Tag.filter_by_recurso(qs, recurso)

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # verifica se existem despesas vinculadas à tag antes de permitir a exclusão
        existe_despesa = RateioDespesa.objects.filter(
            tag=instance,
            despesa__status__in=['COMPLETO', 'INCOMPLETO']
        ).exists()

        if existe_despesa:
            return Response(
                status=400, 
                data={'detail': 'Essa operação não pode ser realizada. Há despesas vinculadas a etiqueta/tag.'})
        self.perform_destroy(instance)
        return Response(status=204)
