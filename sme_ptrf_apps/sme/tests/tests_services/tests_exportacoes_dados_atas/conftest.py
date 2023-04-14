from datetime import date

import pytest
from model_bakery import baker

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.core.files.uploadedfile import SimpleUploadedFile

from sme_ptrf_apps.core.models.ata import Ata

import datetime

@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )

@pytest.fixture
def arquivo_pdf_relacao_bens():
    html_template = get_template('pdf/ata/pdf.html')

    rendered_html = html_template.render({'dados': {}, 'base_static_url': staticfiles_storage.location})

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/ata-pdf.css')])

    filename = 'ata_pdf_%s.pdf'

    return SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')

@pytest.fixture
def ata_prestacao_conta(prestacao_conta, arquivo_pdf_relacao_bens):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta,
        periodo=prestacao_conta.periodo,
        associacao=prestacao_conta.associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretaria',
        comentarios='Comentario teste',
        retificacoes='Retificacao teste',
        justificativa_repasses_pendentes='Justificativa teste',
        parecer_conselho='APROVADA',
        hora_reuniao=datetime.time(12, 30, 0),
        arquivo_pdf=arquivo_pdf_relacao_bens,
        preenchida_em=date(2020, 7, 2)
    )

@pytest.fixture
def queryset_ordered(ata_prestacao_conta):
    return Ata.objects.all().order_by('id')