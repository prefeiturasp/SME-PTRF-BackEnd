from django.db.models import Q
from django_filters import rest_framework as filters

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.core.choices.filtro_informacoes_associacao import FiltroInformacoesAssociacao
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class ParametrizacoesAcoesAssociacaoViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = AcaoAssociacao.objects.all()
    serializer_class = AcaoAssociacaoRetrieveSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('acao__uuid', 'status', 'associacao__uuid')
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = AcaoAssociacao.objects.all().order_by('associacao__nome', 'acao__nome')

        nome = self.request.query_params.get('nome')
        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        if nome is not None:
            qs = qs.filter(Q(associacao__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__codigo_eol__icontains=nome))

        if filtro_informacoes_list:
            if encerradas in filtro_informacoes_list and nao_encerradas in filtro_informacoes_list:
                qs = qs
            elif nao_encerradas in filtro_informacoes_list:
                qs = qs.filter(associacao__data_de_encerramento__isnull=True)

            elif encerradas in filtro_informacoes_list:
                qs = qs.filter(associacao__data_de_encerramento__isnull=False)

        return qs.order_by('associacao__nome', 'acao__nome')
