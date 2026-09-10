from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from waffle.mixins import WaffleFlagMixin
from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoApiSME
from ...models import Mandato
from ..serializers.mandato_vacancia_serializer import MandatoVacanciaSerializer
from ...services import ServicoMandatoVigenteVacancia, ServicoMandatoVacancia
from .docs.mandatos_vacancia_docs import DOCS


@extend_schema_view(**DOCS)
class MandatosVacanciaViewSet(WaffleFlagMixin, viewsets.ModelViewSet):
    """ Viewset necessário pra v2 para flag exclusiva. isolado da v1, que depende da flag `historico-de-membros` (v1)
     e usa MandatoSerializer. Esta passa a usar MandatoVacanciaSerializer """
    waffle_flag = "historico-de-membros-v2"
    permission_classes = [IsAuthenticated & PermissaoApiSME]
    lookup_field = 'uuid'
    queryset = Mandato.objects.all().order_by('-data_inicial')
    serializer_class = MandatoVacanciaSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = self.queryset
        filtro_referencia = self.request.query_params.get('referencia', None)
        if filtro_referencia:
            qs = qs.filter(referencia_mandato__unaccent__icontains=filtro_referencia)
        return qs

    @action(detail=False, methods=['get'], url_path='mandato-vigente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def mandato_vigente(self, request):
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()

        result = MandatoVacanciaSerializer(mandato_vigente).data if mandato_vigente else {"uuid": None}

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='mandatos-anteriores',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def mandatos_anteriores(self, request):
        """ Mesmo critério de filtro da v1 (`MandatosViewSet.mandatos_anteriores`), reimplementado aqui
        para não depender da flag `historico-de-membros` (v1) - só leitura de Mandato, sem Composicao. """
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()

        qs = Mandato.objects.all().order_by('-data_inicial')
        if mandato_vigente:
            qs = qs.filter(data_final__lt=mandato_vigente.data_inicial).exclude(uuid=mandato_vigente.uuid)

        result = MandatoVacanciaSerializer(qs, many=True).data

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='mandato-mais-recente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def mandato_mais_recente(self, request):
        """ Retorna o mandato mais recente, caso exista, ou None caso contrário. """
        mandato_mais_recente = ServicoMandatoVacancia().get_mandato_mais_recente()

        if mandato_mais_recente:
            result = MandatoVacanciaSerializer(mandato_mais_recente, many=False).data
            return Response(result, status=status.HTTP_200_OK)

        result = MandatoVacanciaSerializer(Mandato.objects.none(), many=True).data

        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """ Override do destroy para impedir deleção de mandatos com cargos/composição. """
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()
        mandato_mais_recente = ServicoMandatoVacancia().get_mandato_mais_recente()

        if mandato_mais_recente and obj != mandato_mais_recente:
            resultado = {
                "erro": "ProtectedError",
                "mensagem": "Somente o mandato mais recente pode ser excluído."
            }
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        if obj.composicoes_vacancia_do_mandato.filter(
                cargos_da_composicao_vacancia__ocupante_do_cargo__isnull=False).exists():
            resultado = {
                "erro": "ProtectedError",
                "mensagem": ("Não é possível excluir o período de mandato pois "
                             "já existem membros cadastrados nas associações.")
            }
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            resultado = {
                "erro": "ProtectedError",
                "mensagem": ("Essa operação não pode ser realizada. "
                             "Há dados vinculados a essa ação da referida Associação")
            }
            return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
