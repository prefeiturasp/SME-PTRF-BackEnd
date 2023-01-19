import logging
from django.template.loader import get_template
from django.contrib.staticfiles.storage import staticfiles_storage
from weasyprint import HTML, CSS
from django.core.files.uploadedfile import SimpleUploadedFile
import os

logger = logging.getLogger(__name__)


class ArquivoRelatorioAposAcertos:
    def __init__(self, analise_prestacao_conta, dados_relatorio_apos_acertos):
        self.analise_prestacao_conta = analise_prestacao_conta
        self.dados_relatorio_apos_acertos = dados_relatorio_apos_acertos
        self.html_template = get_template('pdf/relatorio_apos_acertos/pdf.html')
        self.base_static_url = staticfiles_storage.location
        self.path_css = '/css/pdf-relatorio-apos-acertos.css'

    def gerar_relatorio(self):
        rendered_html = self.html_template.render(
            {'dados': self.dados_relatorio_apos_acertos, 'base_static_url': self.base_static_url})

        logger.info(f'base_url: {os.path.basename(self.base_static_url)}')
        logger.info(f'store: {self.base_static_url}')

        pdf_file = HTML(
            string=rendered_html,
            base_url=self.base_static_url
        ).write_pdf(
            stylesheets=[CSS(self.base_static_url + self.path_css)])

        filename = 'relatorio_apos_acertos_pdf_%s.pdf'

        pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
        self.analise_prestacao_conta.finaliza_geracao_arquivo_pdf_relatorio_apos_acertos(pdf)


class ArquivoRelatorioAposAcertosService:

    @classmethod
    def gerar_relatorio(cls, analise_prestacao_conta, dados_relatorio_apos_acertos):
        ArquivoRelatorioAposAcertos(
            analise_prestacao_conta=analise_prestacao_conta, dados_relatorio_apos_acertos=dados_relatorio_apos_acertos
        ).gerar_relatorio()


