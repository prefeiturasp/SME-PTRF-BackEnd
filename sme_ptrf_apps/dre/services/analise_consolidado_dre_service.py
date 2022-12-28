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


class RelatorioDevolucaoAcertos:
    def __init__(self, analise_consolidado, username, previa):
        self.analise_consolidado = analise_consolidado
        self.username = username
        self.previa = previa


    def gerar_arquivo_relatorio_devolucao_acertos(self):
        from sme_ptrf_apps.dre.services import DadosRelatorioDevolucaoAcertosSmeService
        from sme_ptrf_apps.dre.services import ArquivoRelatorioDevolucaoAcertosSmeService

        if self.previa:
            logger.info(f'Gerando prévia do relatorio de devolução acertos sme')
        else:
            logger.info(f'Gerando versão final do relatorio de devolução acertos sme')

        self.analise_consolidado.inicia_geracao_arquivo_pdf_relatorio_devolucao_acertos(self.previa)

        dados_relatorio_devolucao_acertos = DadosRelatorioDevolucaoAcertosSmeService.dados_relatorio_devolucao_acerto(
            analise_consolidado=self.analise_consolidado,
            previa=self.previa,
            username=self.username
        )

        ArquivoRelatorioDevolucaoAcertosSmeService.gerar_relatorio(
            analise_consolidado=self.analise_consolidado,
            dados_relatorio_devolucao_acertos=dados_relatorio_devolucao_acertos
        )
