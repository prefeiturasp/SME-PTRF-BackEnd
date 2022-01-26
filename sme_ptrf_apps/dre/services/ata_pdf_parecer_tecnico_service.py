import os
import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS

LOGGER = logging.getLogger(__name__)
# LOGGER = logging.getLogger("weasyprint")
# LOGGER.addHandler(logging.NullHandler())
# LOGGER.setLevel(40)  # Only show errors, use 50


def gerar_arquivo_ata_parecer_tecnico_pdf(dados_ata, ata):
    LOGGER.info(f'XXXXXXXXXXXXXXXX DADOS DA ATA {dados_ata}')

    html_template = get_template('pdf/ata_parecer_tecnico/pdf.html')

    rendered_html = html_template.render({'dados': dados_ata, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/ata-parecer-tecnico-pdf.css')])

    filename = 'ata_parecer_tecnico_pdf_%s.pdf'

    ata.arquivo_pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    ata.save()

    return ata
