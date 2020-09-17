from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from sme_ptrf_apps.dre.api.serializers.atribuicao_serializer import AtribuicaoSerializer, AtribuicaoCreateSerializer
from sme_ptrf_apps.dre.models import Atribuicao
from sme_ptrf_apps.dre.services.atribuicao_service import (
    desatribuir_em_lote_por_unidade,
    salvar_atualizar_atribuicao_em_lote,
    troca_atribuicao_em_lote,
    copia_atribuicoes_de_um_periodo
)


class AtribuicaoViewset(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Atribuicao.objects.all()
    permission_classes = [AllowAny]
    serializer_class = AtribuicaoSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AtribuicaoSerializer
        else:
            return AtribuicaoCreateSerializer

    @action(detail=False, methods=['post'], url_path='lote')
    def criar_atualizar_atribuicoes_em_lote(self, request, *args, **kwrgs):
        try:
            salvar_atualizar_atribuicao_em_lote(request.data)
        except Exception as err:
            error = {
                'error': "problema_ao_atribuir_unidades",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response("Atribuições feitas com sucesso.", status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='desfazer-lote')
    def desatribuir_em_lote(self, request, *args, **kwrgs):
        try:
            desatribuir_em_lote_por_unidade(request.data)
        except Exception as err:
            error = {
                'error': "problema_ao_desfazer_atribuicoes",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response("Atribuições desfeitas com sucesso.", status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['post'], url_path='troca-lote')
    def troca_atribuicao_em_lote(self, request, *args, **kwrgs):
        try:
            troca_atribuicao_em_lote(request.data)
        except Exception as err:
            error = {
                'error': "problema_ao_trocar_atribuicoes",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response("Atribuições trocadas com sucesso.", status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='copia-periodo')
    def copia_periodo(self, request, *args, **kwrgs):
        try:
            copia_atribuicoes_de_um_periodo(request.data)
        except Exception as err:
            error = {
                'error': "problema_ao_copiar_atribuicoes",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response("Atribuições copiadas com sucesso.", status=status.HTTP_200_OK)
