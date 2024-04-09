from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
)

from sme_ptrf_apps.core.models import Associacao
from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.filters import SearchFilter

from ..serializers.associacao_serializer import (
    AssociacaoListSerializer
)

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class ParametrizacoesAssociacoesViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoListSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filter_fields = ('unidade__dre__uuid', 'unidade__tipo_unidade')
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = Associacao.objects.all().order_by('unidade__tipo_unidade', 'unidade__nome')

        uuid_dre = self.request.query_params.get('unidade__dre__uuid')
        if uuid_dre is not None and uuid_dre != "":
            qs = qs.filter(unidade__dre__uuid=uuid_dre)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(unidade__codigo_eol=nome) | Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome))

        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        if filtro_informacoes_list:
            ids_para_excluir_da_listagem = []
            for associacao in qs:
                excluir_associacao_da_listagem = True
                if Associacao.TAG_ENCERRADA['key'] in filtro_informacoes_list and associacao.foi_encerrada():
                    excluir_associacao_da_listagem = False

                if Associacao.TAG_ENCERRAMENTO_DE_CONTA[
                    'key'] in filtro_informacoes_list and associacao.tem_solicitacao_conta_pendente():
                    excluir_associacao_da_listagem = False

                if excluir_associacao_da_listagem:
                    ids_para_excluir_da_listagem.append(associacao.id)

            qs = qs.exclude(id__in=ids_para_excluir_da_listagem)

        return qs
