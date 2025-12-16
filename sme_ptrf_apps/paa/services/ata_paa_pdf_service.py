import os
import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.models import AtaPaa

LOGGER = logging.getLogger("weasyprint")
LOGGER.addHandler(logging.NullHandler())
LOGGER.setLevel(40)  # Only show errors


def gerar_arquivo_ata_paa_pdf(dados_ata, ata_paa: AtaPaa):
    """
    Gera o arquivo PDF da ata PAA
    """
    try:
        html_template = get_template('pdf/ata_paa/pdf.html')
        
        rendered_html = html_template.render({
            'dados': dados_ata,
            'base_static_url': staticfiles_storage.location
        })
        
        LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
        LOGGER.info(f'store: {staticfiles_storage.location}')
        
        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/ata-paa-pdf.css')]
        )
        
        filename = f'ata_paa_pdf_{ata_paa.uuid}.pdf'
        
        ata_paa.arquivo_pdf = SimpleUploadedFile(
            filename,
            pdf_file,
            content_type='application/pdf'
        )
        ata_paa.save()
        
        return ata_paa
    except Exception as e:
        LOGGER.error(f'Erro ao gerar PDF da ata PAA: {str(e)}', exc_info=True)
        raise

