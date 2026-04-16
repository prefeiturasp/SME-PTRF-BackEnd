import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.services.ata_dados_service import dados_texto_ata

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_simples(associacao, ata_periodo_2020_1, ata_prestacao_conta_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=ata_prestacao_conta_2020_1,
        local_reuniao='Sede da Associação',
        presidente_reuniao='João Silva',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Maria Souza',
        cargo_secretaria_reuniao='Secretária',
        data_reuniao=datetime.date(2020, 7, 15),
        hora_reuniao=datetime.time(14, 30),
        comentarios='Nenhum comentário',
        parecer_conselho='APROVADA',
    )


@pytest.fixture
def ata_periodo_unico(associacao, periodo_factory):
    periodo = periodo_factory(
        referencia='2020.u',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 12, 31),
    )
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=periodo,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
        local_reuniao='Escola',
        presidente_reuniao='Ana Lima',
        cargo_presidente_reuniao='Diretora',
        secretario_reuniao='Carlos Dias',
        cargo_secretaria_reuniao='Vice-diretor',
        data_reuniao=datetime.date(2021, 1, 20),
        hora_reuniao=datetime.time(9, 0),
        comentarios='',
        parecer_conselho='APROVADA',
    )


def test_dados_texto_ata_estrutura(ata_simples):
    resultado = dados_texto_ata(ata_simples, usuario=None)
    chaves_esperadas = [
        'prestacao_conta', 'periodo', 'associacao_nome', 'unidade_cod_eol',
        'unidade_tipo', 'unidade_nome', 'local_reuniao', 'periodo_referencia',
        'presidente_reuniao', 'cargo_presidente_reuniao', 'secretario_reuniao',
        'cargo_secretaria_reuniao', 'data_reuniao_por_extenso', 'comentarios',
        'parecer_conselho', 'usuario', 'hora_reuniao',
    ]
    for chave in chaves_esperadas:
        assert chave in resultado, f"Chave '{chave}' ausente no resultado"


def test_dados_texto_ata_periodo_referencia_numerico(ata_simples):
    resultado = dados_texto_ata(ata_simples, usuario=None)
    assert resultado['periodo_referencia'] == '1° repasse de 2020'


def test_dados_texto_ata_periodo_referencia_unico(ata_periodo_unico):
    resultado = dados_texto_ata(ata_periodo_unico, usuario=None)
    assert resultado['periodo_referencia'] == 'repasse único de 2020'


def test_dados_texto_ata_hora_formatada(ata_simples):
    resultado = dados_texto_ata(ata_simples, usuario=None)
    assert resultado['hora_reuniao'] == '14:30'


def test_dados_texto_ata_local_reuniao(ata_simples):
    resultado = dados_texto_ata(ata_simples, usuario=None)
    assert resultado['local_reuniao'] == 'Sede da Associação'


def test_dados_texto_ata_usuario_passado(ata_simples):
    usuario = object()
    resultado = dados_texto_ata(ata_simples, usuario=usuario)
    assert resultado['usuario'] is usuario


def test_dados_texto_ata_data_reuniao_por_extenso(ata_simples):
    resultado = dados_texto_ata(ata_simples, usuario=None)
    assert 'julho' in resultado['data_reuniao_por_extenso']
    assert '2020' in resultado['data_reuniao_por_extenso'] \
        or 'dois mil' in resultado['data_reuniao_por_extenso'].lower()


def test_dados_texto_ata_sem_prestacao_conta(associacao, ata_periodo_2020_1):
    ata = baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
        hora_reuniao=datetime.time(10, 0),
        data_reuniao=datetime.date(2020, 3, 10),
    )
    resultado = dados_texto_ata(ata, usuario=None)
    assert resultado['prestacao_conta'] == '___'
