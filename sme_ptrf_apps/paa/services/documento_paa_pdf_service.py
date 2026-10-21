import os
import logging
from typing import Optional

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.models import DocumentoPaa, Paa
from sme_ptrf_apps.paa.services.dados_documento_paa_service import gerar_dados_documento_paa

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_documento_paa_pdf(
    paa: Paa,
    documento_paa: DocumentoPaa,
    usuario: str,
    previa: bool = False,
    alteracoes: Optional[dict] = None,
    **kwargs: object,
) -> None:
    """Gera o PDF do documento PAA e salva o arquivo no modelo informado.

    Args:
        paa: PAA utilizado para montar os dados do documento.
        documento_paa: Documento que receberá o arquivo PDF gerado.
        usuario: Identificação do usuário responsável pela geração.
        previa: Indica se o documento deve ser gerado como prévia.
        alteracoes: Alterações que devem ser consideradas na geração do
            documento.
        **kwargs: Opções adicionais encaminhadas para a geração dos dados.
    """
    dados = gerar_dados_documento_paa(
        paa,
        usuario,
        previa,
        alteracoes=alteracoes,
        gerado_em=documento_paa.gerado_em,
        **kwargs
    )

    html_template = get_template('pdf/paa/documento/pdf-horizontal.html')

    rendered_html = html_template.render(
        {'dados': dados, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-documento-paa-horizontal.css')])

    filename = 'documento_paa_pdf_%s.pdf'

    documento_paa.arquivo_pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    documento_paa.save()
