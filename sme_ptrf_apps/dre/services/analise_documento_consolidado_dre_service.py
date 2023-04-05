import logging

from sme_ptrf_apps.dre.models import (
    AnaliseDocumentoConsolidadoDre,
    DocumentoAdicional,
    RelatorioConsolidadoDRE,
    AtaParecerTecnico
)
from django.core.exceptions import ValidationError
from rest_framework import status
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AnaliseDocumentoConsolidadoDreService:

    def __init__(self, analise_atual_consolidado):
        self.__analise_atual_consolidado = analise_atual_consolidado
        self.__tipos_documentos_validos = ['RELATORIO_CONSOLIDADO', 'ATA_PARECER_TECNICO', 'DOCUMENTO_ADICIONAL']
        self.response = {
            "mensagem": "Status de documento conferido foi aplicado com sucesso.",
            "status": status.HTTP_200_OK
        }

    @property
    def analise_atual_consolidado(self):
        return self.__analise_atual_consolidado

    @property
    def tipos_documentos_validos(self):
        return self.__tipos_documentos_validos

    def set_error_response(self, tipo_de_erro, mensagem):
        self.response['erro'] = tipo_de_erro
        self.response["mensagem"] = mensagem
        self.response["status"] = status.HTTP_400_BAD_REQUEST


class CriarAcerto(AnaliseDocumentoConsolidadoDreService):
    def __init__(self, analise_atual_consolidado, tipo_documento, documento_uuid, detalhamento):
        super().__init__(analise_atual_consolidado)
        self.__tipo_documento = tipo_documento
        self.__documento_uuid = documento_uuid
        self.__detalhamento = detalhamento

    @property
    def tipo_documento(self):
        return self.__tipo_documento

    @property
    def documento_uuid(self):
        return self.__documento_uuid

    @property
    def detalhamento(self):
        return self.__detalhamento

    def criar_acerto_em_documento(self):
        if self.tipo_documento == 'RELATORIO_CONSOLIDADO':
            try:
                documento = RelatorioConsolidadoDRE.objects.get(uuid=self.documento_uuid)
                analise_documento, created = AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                    analise_consolidado_dre=self.analise_atual_consolidado,
                    relatorio_consolidao_dre=documento,
                    defaults={'detalhamento': self.detalhamento, 'resultado': 'AJUSTE'}
                )
                return analise_documento
            except (AnaliseDocumentoConsolidadoDre.DoesNotExist, RelatorioConsolidadoDRE.DoesNotExist, ValidationError):
                return False

        elif self.tipo_documento == 'ATA_PARECER_TECNICO':
            try:
                documento = AtaParecerTecnico.objects.get(uuid=self.documento_uuid)
                analise_documento, created = AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                    analise_consolidado_dre=self.analise_atual_consolidado,
                    ata_parecer_tecnico=documento,
                    defaults={'detalhamento': self.detalhamento, 'resultado': 'AJUSTE'}
                )
                return analise_documento
            except (AnaliseDocumentoConsolidadoDre.DoesNotExist, AtaParecerTecnico.DoesNotExist, ValidationError):
                return False

        else:
            try:
                documento = DocumentoAdicional.objects.get(uuid=self.documento_uuid)
                analise_documento, created = AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                    analise_consolidado_dre=self.analise_atual_consolidado,
                    documento_adicional=documento,
                    defaults={'detalhamento': self.detalhamento, 'resultado': 'AJUSTE'}
                )
                return analise_documento
            except (AnaliseDocumentoConsolidadoDre.DoesNotExist, DocumentoAdicional.DoesNotExist, ValidationError):
                return False

    def retorna_acerto_documento(self):
        analise_documento = self.criar_acerto_em_documento()

        return analise_documento


class MarcarComoCorreto(AnaliseDocumentoConsolidadoDreService):
    def __init__(self, analise_atual_consolidado, documentos):
        super().__init__(analise_atual_consolidado)
        self.__documentos = documentos

    @property
    def documentos(self):
        return self.__documentos

    def marcar_documentos_como_corretos(self):

        for documento in self.documentos:

            if documento['tipo_documento'] not in self.tipos_documentos_validos:
                self.set_error_response('tipo_de_documento_invalido', f"O tipo de documento {documento['tipo_documento']} é inválido as opções são: RELATORIO_CONSOLIDADO, ATA_PARECER_TECNICO ou DOCUMENTO_ADICIONAL")
                break

            if documento['tipo_documento'] == 'RELATORIO_CONSOLIDADO':
                try:
                    doc = RelatorioConsolidadoDRE.objects.get(uuid=documento['uuid_documento'])
                    AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                        analise_consolidado_dre=self.analise_atual_consolidado,
                        relatorio_consolidao_dre=doc,
                        defaults={'detalhamento': "", 'resultado': 'CORRETO'}
                    )
                except (AnaliseDocumentoConsolidadoDre.DoesNotExist, RelatorioConsolidadoDRE.DoesNotExist, ValidationError):
                    self.set_error_response('erro_ao_marcar_como_correto', f"Não foi possível marcar o Documento Relatorio Consolidado de uuid {documento['uuid_documento']} como correto!")
                    break

            elif documento['tipo_documento'] == 'ATA_PARECER_TECNICO':
                try:
                    doc = AtaParecerTecnico.objects.get(uuid=documento['uuid_documento'])
                    AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                        analise_consolidado_dre=self.analise_atual_consolidado,
                        ata_parecer_tecnico=doc,
                        defaults={'detalhamento': "", 'resultado': 'CORRETO'}
                    )
                except (AnaliseDocumentoConsolidadoDre.DoesNotExist, AtaParecerTecnico.DoesNotExist, ValidationError):
                    self.set_error_response('erro_ao_marcar_como_correto', f"Não foi possível marcar o Documento Ata de Parecer Técnico de uuid {documento['uuid_documento']} como correto!")
                    break
            else:
                try:
                    doc = DocumentoAdicional.objects.get(uuid=documento['uuid_documento'])
                    AnaliseDocumentoConsolidadoDre.objects.update_or_create(
                        analise_consolidado_dre=self.analise_atual_consolidado,
                        documento_adicional=doc,
                        defaults={'detalhamento': "", 'resultado': 'CORRETO'}
                    )
                except (AnaliseDocumentoConsolidadoDre.DoesNotExist, DocumentoAdicional.DoesNotExist, ValidationError):
                    self.set_error_response('erro_ao_marcar_como_correto', f"Não foi possível marcar o Documento Adicional de uuid {documento['uuid_documento']} como correto!")
                    break

        return self.response

    def retorna_documentos_marcados_como_correto(self):
        return self.marcar_documentos_como_corretos()


class MarcarComoNaoConferido(AnaliseDocumentoConsolidadoDreService):
    def __init__(self, analise_atual_consolidado, uuids_analises_documentos):
        super().__init__(analise_atual_consolidado)
        self.__uuids_analises_documentos = uuids_analises_documentos

    @property
    def uuids_analises_documentos(self):
        return self.__uuids_analises_documentos

    def marcar_documentos_como_nao_conferidos(self):

        for uuid in self.uuids_analises_documentos:
            try:
                analise = AnaliseDocumentoConsolidadoDre.objects.get(uuid=uuid)
                analise.delete()
            except (AnaliseDocumentoConsolidadoDre.DoesNotExist, ValidationError):
                self.set_error_response('erro_ao_marcar_como_nao_conferido', f"Não foi possível marcar o Documento de uuid {uuid} como nao conferido!")
                break

        return self.response

    def retorna_documentos_nao_conferidos(self):
        return self.marcar_documentos_como_nao_conferidos()


class DownloadDocumento:
    def __init__(self, documento_uuid, tipo_documento):
        self.__documento_uuid = documento_uuid
        self.__tipo_documento = tipo_documento

    @property
    def documento_uuid(self):
        return self.__documento_uuid

    @property
    def tipo_documento(self):
        return self.__tipo_documento

    def download_documento(self):
        if self.tipo_documento == 'RELATORIO_CONSOLIDADO':
            try:
                relatorio_fisico_financeiro = RelatorioConsolidadoDRE.by_uuid(self.documento_uuid)
            except (ValidationError, Exception):
                return False

            try:
                filename = 'relatorio_fisico_financeiro_dre.pdf'
                response = HttpResponse(
                    open(relatorio_fisico_financeiro.arquivo.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
            except (ValidationError, Exception):
                return False
        else:
            try:
                ata = AtaParecerTecnico.by_uuid(self.documento_uuid)
            except (ValidationError, Exception):
                return False

            try:
                filename = 'ata_parecer_tecnico.pdf'
                response = HttpResponse(
                    open(ata.arquivo_pdf.path, 'rb'),
                    content_type='application/pdf'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
            except (ValidationError, Exception):
                return False

    def retorna_download_documento(self):
        return self.download_documento()
