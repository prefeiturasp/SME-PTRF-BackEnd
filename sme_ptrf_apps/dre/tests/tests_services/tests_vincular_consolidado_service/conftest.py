import pytest

from datetime import date
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile

from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def vcs_periodo_2022_1():
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
    )


@pytest.fixture
def vcs_dre_ipiranga():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='DRE IPIRANGA',
        sigla='I'
    )


@pytest.fixture
def vcs_consolidado_dre_ipiranga_2022_1(vcs_periodo_2022_1, vcs_dre_ipiranga):
    return baker.make(
        'ConsolidadoDRE',
        dre=vcs_dre_ipiranga,
        periodo=vcs_periodo_2022_1,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def vcs_consolidado_dre_ipiranga_2022_1_parcial_1(vcs_periodo_2022_1, vcs_dre_ipiranga):
    return baker.make(
        'ConsolidadoDRE',
        dre=vcs_dre_ipiranga,
        periodo=vcs_periodo_2022_1,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        eh_parcial=True,
        sequencia_de_publicacao=1
    )


@pytest.fixture
def vcs_consolidado_dre_ipiranga_2022_1_parcial_2(vcs_periodo_2022_1, vcs_dre_ipiranga):
    return baker.make(
        'ConsolidadoDRE',
        dre=vcs_dre_ipiranga,
        periodo=vcs_periodo_2022_1,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        eh_parcial=True,
        sequencia_de_publicacao=2
    )


@pytest.fixture
def vcs_relatorio_dre_consolidado_gerado_total_desvinculado(vcs_periodo_2022_1, vcs_dre_ipiranga, tipo_conta_cartao, arquivo):
    return baker.make(
        'RelatorioConsolidadoDre',
        dre=vcs_dre_ipiranga,
        tipo_conta=tipo_conta_cartao,
        periodo=vcs_periodo_2022_1,
        arquivo=arquivo,
        status='GERADO_TOTAL',
        consolidado_dre=None,
    )


@pytest.fixture
def vcs_ata_parecer_tecnico_desvinculada(vcs_dre_ipiranga, vcs_periodo_2022_1):
    return baker.make(
        'AtaParecerTecnico',
        arquivo_pdf=None,
        periodo=vcs_periodo_2022_1,
        dre=vcs_dre_ipiranga,
        status_geracao_pdf='NAO_GERADO',
        numero_ata=1,
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        comentarios='Teste',
        consolidado_dre=None,
        sequencia_de_publicacao=None
    )


@pytest.fixture
def vcs_arquivo_lauda():
    return SimpleUploadedFile(f'arquivo.txt', bytes(f'CONTEUDO TESTE TESTE TESTE', encoding="utf-8"))


@pytest.fixture
def vcs_visao_dre():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def vcs_usuario_lauda(
    vcs_dre_ipiranga,
    vcs_visao_dre
):
    from django.contrib.auth import get_user_model

    senha = 'Sgp0418'
    login = '8989877'
    email = 'teste.api@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(vcs_dre_ipiranga)
    user.visoes.add(vcs_visao_dre)
    user.save()
    return user


@pytest.fixture
def vcs_lauda_desvinculada(
    vcs_arquivo_lauda,
    vcs_dre_ipiranga,
    vcs_periodo_2022_1,
    tipo_conta_cartao,
    vcs_usuario_lauda

):
    return baker.make(
        'Lauda',
        arquivo_lauda_txt=vcs_arquivo_lauda,
        consolidado_dre=None,
        dre=vcs_dre_ipiranga,
        periodo=vcs_periodo_2022_1,
        tipo_conta=tipo_conta_cartao,
        usuario=vcs_usuario_lauda,
        status='GERADA_TOTAL',
    )
