import logging
import uuid
import copy

from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AnaliseConsolidadoDreService:
    analise_origem = None
    analise_destino = None

    def __init__(self, analise_origem, analise_destino):
        self.analise_origem = analise_origem
        self.analise_destino = analise_destino
        self.response = {
            "mensagem": "A analise de consolidado foi criada com sucesso!",
            "status": status.HTTP_200_OK
        }

    def set_error_response(self, tipo_de_erro, mensagem):
        self.response['erro'] = tipo_de_erro
        self.response["mensagem"] = mensagem
        self.response["status"] = status.HTTP_400_BAD_REQUEST

    def copia_documentos_consolidado_entre_analises(self): # TESTE LINIKER
        for analise_documento in self.analise_origem.analises_de_documentos_da_analise_do_consolidado.all():
            self.nova_analise = copy.deepcopy(analise_documento)
            self.nova_analise.pk = None
            self.nova_analise.uuid = uuid.uuid4()
            self.nova_analise.analise_consolidado_dre = self.analise_destino
            self.nova_analise.save()

    def copia_comentarios_consolidado_entre_analises(self): # TESTE LINIKER
        for analise_comentario in self.analise_origem.consolidado_dre.comentarios_de_analise_do_consolidado_dre.all():
            self.nova_analise = copy.deepcopy(analise_comentario)
            self.nova_analise.pk = None
            self.nova_analise.uuid = uuid.uuid4()
            self.nova_analise.analise_consolidado_dre = self.analise_destino
            self.nova_analise.save()

    def copia_info_consolidado_entre_analises(self): # TESTE LINIKER
        x = 1

    def copia_ajustes_consolidado_entre_analises(self): #TESTE LINIKER
        import ipdb; ipdb.set_trace();
        self.copia_documentos_consolidado_entre_analises()
        self.copia_comentarios_consolidado_entre_analises()
        self.copia_info_consolidado_entre_analises()

        return self.nova_analise
