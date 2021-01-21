from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.core.api.serializers import ArquivoSerializer
from sme_ptrf_apps.core.models import Arquivo


class ArquivoViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    lookup_field = "uuid"
    queryset = Arquivo.objects.all().order_by('-criado_em')
    serializer_class = ArquivoSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('status',)

    def get_queryset(self):
        qs = Arquivo.objects.all()

        data_execucao = self.request.query_params.get('data_execucao')
        if data_execucao is not None:
            qs = qs.filter(ultima_execucao=data_execucao)

        identificador = self.request.query_params.get('identificador')
        if identificador is not None:
            qs = qs.filter(Q(identificador__unaccent__icontains=identificador))

        return qs


    @action(detail=False, url_path='tabelas')
    def tabelas(self, _):
        result = {
            'status': Arquivo.status_to_json(),
            'tipos_cargas': Arquivo.tipos_cargas_to_json(),
            'tipos_delimitadores': Arquivo.delimitadores_to_json()
        }
        return Response(result)
