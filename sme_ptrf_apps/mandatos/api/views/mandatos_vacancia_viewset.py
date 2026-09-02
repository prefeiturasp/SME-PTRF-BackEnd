from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from waffle.mixins import WaffleFlagMixin
from drf_spectacular.utils import extend_schema_view


from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from ...models import Mandato
from ..serializers.mandato_serializer import MandatoSerializer
from ...services import ServicoMandatoVigenteVacancia
from .docs.mandatos_vacancia_docs import DOCS


@extend_schema_view(**DOCS)
class MandatosVacanciaViewSet(WaffleFlagMixin, GenericViewSet):
    """ Viewset necessário pra v2 para flag exclusiva """
    waffle_flag = "historico-de-membros-v2"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Mandato.objects.all().order_by('-data_inicial')
    serializer_class = MandatoSerializer

    @action(detail=False, methods=['get'], url_path='mandato-vigente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def mandato_vigente(self, request):
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()

        result = MandatoSerializer(mandato_vigente).data if mandato_vigente else {"uuid": None}

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

        result = MandatoSerializer(qs, many=True).data

        return Response(result, status=status.HTTP_200_OK)
