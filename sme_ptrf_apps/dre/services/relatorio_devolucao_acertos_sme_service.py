import logging
from django.template.loader import get_template
from django.contrib.staticfiles.storage import staticfiles_storage
from weasyprint import HTML, CSS
from django.core.files.uploadedfile import SimpleUploadedFile
import os

logger = logging.getLogger(__name__)


class ArquivoRelatorioDevolucaoAcertosSme:

    def __init__(self, analise_consolidado, dados_relatorio_devolucao_acertos):
        self.analise_consolidado = analise_consolidado
        self.dados_relatorio_devolucao_acertos = dados_relatorio_devolucao_acertos
        self.html_template = get_template('pdf/relatorio_devolucao_acertos_sme/pdf.html')
        self.base_static_url = staticfiles_storage.location
        self.path_css = '/css/pdf-relatorio-apos-acertos.css'

    def gerar_relatorio(self):
        rendered_html = self.html_template.render(
            {'dados': self.dados_relatorio_devolucao_acertos, 'base_static_url': self.base_static_url})

        logger.info(f'base_url: {os.path.basename(self.base_static_url)}')
        logger.info(f'store: {self.base_static_url}')

        pdf_file = HTML(
            string=rendered_html,
            base_url=self.base_static_url
        ).write_pdf(
            stylesheets=[CSS(self.base_static_url + self.path_css)])

        filename = 'relatorio_devolucao_acertos_pdf_%s.pdf'

        pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
        self.analise_consolidado.finaliza_geracao_arquivo_pdf_relatorio_devolucao_acertos(pdf)


class ArquivoRelatorioDevolucaoAcertosSmeService:

    @classmethod
    def gerar_relatorio(cls, analise_consolidado, dados_relatorio_devolucao_acertos):
        ArquivoRelatorioDevolucaoAcertosSme(
            analise_consolidado=analise_consolidado, dados_relatorio_devolucao_acertos=dados_relatorio_devolucao_acertos
        ).gerar_relatorio()
