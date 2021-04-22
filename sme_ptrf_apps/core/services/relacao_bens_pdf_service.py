import os
import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS

# LOGGER = logging.getLogger(__name__)
LOGGER = logging.getLogger("weasyprint")
LOGGER.addHandler(logging.NullHandler())
LOGGER.setLevel(40)  # Only show errors, use 50


def gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens, relacao_bens):

    html_template = get_template('pdf/relacao_de_bens/pdf.html')

    rendered_html = html_template.render({'dados': dados_relacao_de_bens, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/relacao-de-bens-pdf.css')])

    filename = 'relacao_de_bens_pdf_%s.pdf'

    relacao_bens.arquivo_pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    relacao_bens.save()

