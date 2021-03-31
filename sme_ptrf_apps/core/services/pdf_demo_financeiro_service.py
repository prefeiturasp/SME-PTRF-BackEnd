import os
import logging

from tempfile import NamedTemporaryFile

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string, get_template
from django.core.files import File
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS

LOGGER = logging.getLogger(__name__)


def gerar_pdf_demonstrativo_financeiro(dados_demonstrativo, demostrativo_financeiro):
    html_template = get_template('pdf/demonstrativo_financeiro/pdf.html')

    rendered_html = html_template.render({'dados': dados_demonstrativo, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-demo-financeiro.css')])

    filename = 'demonstrativo_financeiro_pdf_%s.pdf'

    demostrativo_financeiro.arquivo_pdf = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    demostrativo_financeiro.save()

    # html_string = render_to_string(
    #     'pdf/demonstrativo_financeiro/pdf.html',
    #     {
    #         "dados": dados_demonstrativo
    #     }
    # ).encode(encoding="UTF-8")

    # pdf = HTML(string=html_string).write_pdf()
    #
    # with NamedTemporaryFile() as tmp:
    #     pdf.save(tmp.name)
    #
    #     demostrativo_financeiro.arquivo_pdf.save(name=filename % demostrativo_financeiro.pk, content=File(tmp))
    #
    #
