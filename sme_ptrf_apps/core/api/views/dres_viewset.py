import logging

from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao

from ...models import Unidade, Associacao, Periodo
from ..serializers import UnidadeSerializer

logger = logging.getLogger(__name__)


class DresViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet, ):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Unidade.dres.all()
    filters = (filters.DjangoFilterBackend, SearchFilter,)
    serializer_class = UnidadeSerializer
    filter_fields = ('codigo_eol')

    def get_queryset(self):
        qs = Unidade.dres.all().order_by('codigo_eol')

        codigo_eol = self.request.query_params.get('codigo_eol')
        if codigo_eol:
            qs = qs.filter(codigo_eol=codigo_eol).order_by('codigo_eol')

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(nome__unaccent__icontains=search)

        return qs

    @action(detail=True, url_path='qtd-unidades',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def qtd_unidades(self, request, uuid=None):
        dre = self.get_object()

        # Determina o período
        periodo_uuid = self.request.query_params.get('periodo__uuid')

        if periodo_uuid:
            try:
                periodo = Periodo.objects.get(uuid=periodo_uuid)
            except (Periodo.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            periodo = None

        if periodo:
            quantidade = Associacao.get_associacoes_ativas_no_periodo(periodo=periodo, dre=dre).count()
            logger.info('Quantidade de unidades da DRE %r no período %r: %r', dre, periodo, quantidade)
        else:
            quantidade = dre.unidades_da_dre.count()
            logger.info('Quantidade de unidades da DRE %r: %r', dre, quantidade)

        result = {
            "uuid": f'{uuid}',
            "qtd_unidades": quantidade,
        }

        return Response(result)
