import pytest
from model_bakery import baker

from sme_ptrf_apps.core.services.ata_dados_service import cria_cabecalho

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_apresentacao(associacao, ata_periodo_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
    )


@pytest.fixture
def ata_retificacao(associacao, ata_periodo_2020_1, ata_prestacao_conta_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='RETIFICACAO',
        prestacao_conta=ata_prestacao_conta_2020_1,
    )


def test_cria_cabecalho_tipo_apresentacao(ata_apresentacao):
    cabecalho = cria_cabecalho(ata_apresentacao)
    assert cabecalho['tipo_ata'] == 'Apresentação'


def test_cria_cabecalho_tipo_retificacao(ata_retificacao):
    cabecalho = cria_cabecalho(ata_retificacao)
    assert cabecalho['tipo_ata'] == 'Retificação'


def test_cria_cabecalho_estrutura(ata_apresentacao):
    cabecalho = cria_cabecalho(ata_apresentacao)
    assert 'titulo' in cabecalho
    assert 'recurso' in cabecalho
    assert 'subtitulo' in cabecalho
    assert 'tipo_ata' in cabecalho
    assert 'periodo_referencia' in cabecalho
    assert 'periodo_data_inicio' in cabecalho
    assert 'periodo_data_fim' in cabecalho


def test_cria_cabecalho_subtitulo(ata_apresentacao):
    cabecalho = cria_cabecalho(ata_apresentacao)
    assert cabecalho['subtitulo'] == 'Prestação de Contas'


def test_cria_cabecalho_periodo_referencia(ata_apresentacao, ata_periodo_2020_1):
    cabecalho = cria_cabecalho(ata_apresentacao)
    assert cabecalho['periodo_referencia'] == '2020.1'


def test_cria_cabecalho_datas_formatadas(ata_apresentacao):
    cabecalho = cria_cabecalho(ata_apresentacao)
    assert cabecalho['periodo_data_inicio'] == '01/01/2020'
    assert cabecalho['periodo_data_fim'] == '30/06/2020'


def test_cria_cabecalho_sem_data_fim(associacao, ata_periodo_2020_1):
    ata_periodo_2020_1.data_fim_realizacao_despesas = None
    ata_periodo_2020_1.save()
    ata = baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
    )
    cabecalho = cria_cabecalho(ata)
    assert cabecalho['periodo_data_fim'] == '___'
