import os
from collections import namedtuple

from allauth.utils import build_absolute_uri
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from weasyprint import HTML


def gerar_pdf_demonstrativo_financeiro(dados_demonstrativo):

    filename = 'demonstrativo_financeiro_pdf_%s.pdf'

    html_string = render_to_string(
        'pdf/demonstrativo_financeiro/pdf.html',
        {
            "dados": dados_demonstrativo
        }
    ).encode(encoding="UTF-8")

    html_pdf = HTML(string=html_string, base_url=os.path.basename(staticfiles_storage.location)).write_pdf('/home/ipm/pdf.pdf')

    #
    # with NamedTemporaryFile() as tmp:
    #     xlsx.save(tmp.name)
    #
    #     demonstrativo_financeiro, _ = DemonstrativoFinanceiro.objects.update_or_create(
    #         acao_associacao=acao_associacao,
    #         conta_associacao=conta_associacao,
    #         prestacao_conta=prestacao
    #     )
    #
    #     demonstrativo_financeiro.arquivo.save(name=filename % demonstrativo_financeiro.pk, content=File(tmp))
    #
    #
