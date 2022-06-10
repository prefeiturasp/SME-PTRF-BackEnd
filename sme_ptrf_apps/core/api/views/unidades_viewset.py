from django_filters import rest_framework as filters
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import UnidadeSerializer, UnidadeListComNomeSerializer
from ...models import Unidade
from ...services import monta_unidade_para_atribuicao
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
)


class UnidadesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Unidade.objects.all().order_by("tipo_unidade", "nome")
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filters = (filters.DjangoFilterBackend, SearchFilter,)
    serializer_class = UnidadeSerializer
    filter_fields = ('tipo_unidade', 'codigo_eol', 'dre__uuid')

    def get_queryset(self):
        qs = Unidade.objects.all()

        tipo_unidade = self.request.query_params.get('tipo_unidade')
        if tipo_unidade:
            qs = qs.filter(tipo_unidade=tipo_unidade)

        codigo_eol = self.request.query_params.get('codigo_eol')
        if codigo_eol:
            qs = qs.filter(codigo_eol=codigo_eol)

        tecnico = self.request.query_params.get('tecnico')
        if tecnico:
            qs = qs.filter(atribuicoes__tecnico__uuid=tecnico)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(Q(codigo_eol=search) | Q(nome__unaccent__icontains=search))

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return UnidadeListComNomeSerializer
        else:
            return UnidadeSerializer

    @action(detail=False, url_path='para-atribuicao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def para_atribuicao(self, request, *args, **kwargs):
        dre_uuid = request.query_params.get('dre_uuid')
        periodo = request.query_params.get('periodo')

        if not dre_uuid or not periodo:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        list_unidades = monta_unidade_para_atribuicao(self.get_queryset(), dre_uuid, periodo)
        return Response(list_unidades)
