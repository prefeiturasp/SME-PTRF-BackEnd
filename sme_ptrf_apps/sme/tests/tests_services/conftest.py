import datetime
import pytest

from model_bakery import baker
from django.contrib.auth import get_user_model
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.receitas.models.motivo_estorno import MotivoEstorno
from sme_ptrf_apps.core.models import FechamentoPeriodo, PrestacaoConta, RelacaoBens

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template

from django.core.files.uploadedfile import SimpleUploadedFile

from weasyprint import HTML, CSS


pytestmark = pytest.mark.django_db


@pytest.fixture
def motivo_estorno_01():
    return baker.make(
        'MotivoEstorno',
        motivo="Motivo de estorno 01"
    )


@pytest.fixture
def motivo_estorno_02():
    return baker.make(
        'MotivoEstorno',
        motivo="Motivo de estorno 02"
    )


@pytest.fixture
def receita_queryset(associacao, conta_associacao, acao_associacao, tipo_receita, motivo_estorno_01, motivo_estorno_02):
    baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 28),
        valor=50.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        motivos_estorno=[motivo_estorno_01, motivo_estorno_02],
        _quantity=2
    )
    return Receita.objects.all()


@pytest.fixture
def usuario_para_teste():
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(
        username=login,
        password=senha,
        email=email
    )
    user.save()

    return user

@pytest.fixture
def periodo_2020_1():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
        data_prevista_repasse=datetime.date(2020, 1, 1),
        data_inicio_prestacao_contas=datetime.date(2020, 7, 1),
        data_fim_prestacao_contas=datetime.date(2020, 7, 10),
    )

@pytest.fixture
def prestacao_conta_2020_1(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        status=PrestacaoConta.STATUS_NAO_RECEBIDA
    )

@pytest.fixture
def fechamento_periodo_queryset(prestacao_conta_2020_1, periodo_2020_1, associacao, conta_associacao, acao_associacao):
    baker.make(
        'FechamentoPeriodo',
        prestacao_conta=prestacao_conta_2020_1,
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )

    baker.make(
        'FechamentoPeriodo',
        prestacao_conta=prestacao_conta_2020_1,
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
    )

    return FechamentoPeriodo.objects.all()

@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )

@pytest.fixture
def arquivo_pdf_relacao_bens():
    html_template = get_template('pdf/relacao_de_bens/pdf.html')
    rendered_html = html_template.render(
        {'dados': {}, 'base_static_url': staticfiles_storage.location})

    pdf_file = HTML(
        string=rendered_html,
        base_url=staticfiles_storage.location
    ).write_pdf(
        stylesheets=[CSS(staticfiles_storage.location + '/css/relacao-de-bens-pdf.css')])

    filename = 'relacao_de_bens_pdf_%s.pdf'

    return SimpleUploadedFile(filename, pdf_file, content_type='application/pdf')

@pytest.fixture
def relacao_bens_queryset(prestacao_conta_2020_1, conta_associacao, arquivo_pdf_relacao_bens):
    baker.make(
        'RelacaoBens',
        arquivo_pdf=arquivo_pdf_relacao_bens,
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao_conta_2020_1,
        periodo_previa=None
    )

    baker.make(
        'RelacaoBens',
        arquivo_pdf=arquivo_pdf_relacao_bens,
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao_conta_2020_1,
        periodo_previa=None
    )

    return RelacaoBens.objects.all()
