import os
import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS

from sme_ptrf_apps.core.models import TipoConta

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_demonstrativo_execucao_fisico_financeiro_pdf(dados_demonstrativo, demostrativo_financeiro):

    html_template = get_template('pdf/demonstrativo_execucao_fisico_financeiro/pdf-horizontal.html')

    tipos_de_contas = TipoConta.objects.all()

    tipos_de_conta_list = []

    for tipo_de_conta in tipos_de_contas:
        objeto_tipo_de_conta = {
            "nome": tipo_de_conta.nome
        }

        tipos_de_conta_list.append(objeto_tipo_de_conta)

    rendered_html = html_template.render({'dados': dados_demonstrativo, 'tipos_de_conta_list': tipos_de_conta_list, 'base_static_url': staticfiles_storage.location})

    LOGGER.info(f'base_url: {os.path.basename(staticfiles_storage.location)}')
    LOGGER.info(f'store: {staticfiles_storage.location}')

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-demo-execucao-fisico-financeiro-horizontal.css')])

    filename = 'demonstrativo_financeiro_pdf_%s.pdf'

    demostrativo_financeiro.arquivo = SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')
    demostrativo_financeiro.save()

