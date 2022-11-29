import logging

from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AnaliseConsolidadoDreService:
    def __init__(self, analise_consolidado_dre):
        self.__consolidado_dre = analise_consolidado_dre
        self.response = {
            "mensagem": "A analise de consolidado foi criada com sucesso!",
            "status": status.HTTP_200_OK
        }

    @property
    def analise_atual_consolidado(self):
        return self.__analise_atual_consolidado

    @property
    def analise_historico_consolidado(self):
        return self.__analise_historico_consolidado

    def set_error_response(self, tipo_de_erro, mensagem):
        self.response['erro'] = tipo_de_erro
        self.response["mensagem"] = mensagem
        self.response["status"] = status.HTTP_400_BAD_REQUEST
