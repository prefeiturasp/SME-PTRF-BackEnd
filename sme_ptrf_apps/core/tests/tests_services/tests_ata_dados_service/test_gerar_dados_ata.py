import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.services.ata_dados_service import gerar_dados_ata

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_completa(associacao, ata_periodo_2020_1, ata_prestacao_conta_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
        local_reuniao='Sede da Associação',
        presidente_reuniao='João Silva',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Maria Souza',
        cargo_secretaria_reuniao='Secretária',
        data_reuniao=datetime.date(2020, 7, 15),
        hora_reuniao=datetime.time(14, 30),
        comentarios='Sem comentários',
        parecer_conselho='APROVADA',
        retificacoes='',
        justificativa_repasses_pendentes='',
    )


@pytest.fixture
def ata_retificacao_completa(associacao, ata_periodo_2020_1, ata_prestacao_conta_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='RETIFICACAO',
        prestacao_conta=ata_prestacao_conta_2020_1,
        local_reuniao='Escola Municipal',
        presidente_reuniao='Ana Lima',
        cargo_presidente_reuniao='Diretora',
        secretario_reuniao='Carlos Dias',
        cargo_secretaria_reuniao='Vice-diretor',
        data_reuniao=datetime.date(2020, 8, 10),
        hora_reuniao=datetime.time(10, 0),
        comentarios='',
        parecer_conselho='APROVADA',
        retificacoes='Correção de valor',
        justificativa_repasses_pendentes='',
    )


def test_gerar_dados_ata_retorna_estrutura_completa(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    assert 'cabecalho' in resultado
    assert 'retificacoes' in resultado
    assert 'devolucoes_ao_tesouro' in resultado
    assert 'info_financeira_ata' in resultado
    assert 'dados_da_ata' in resultado
    assert 'dados_texto_da_ata' in resultado
    assert 'presentes_na_ata' in resultado
    assert 'repasses_pendentes' in resultado
    assert 'justificativa_repasses_pendentes' in resultado


def test_gerar_dados_ata_dados_da_ata_e_a_propria_ata(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    assert resultado['dados_da_ata'] is ata_completa


def test_gerar_dados_ata_cabecalho_tipo_apresentacao(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    assert resultado['cabecalho']['tipo_ata'] == 'Apresentação'


def test_gerar_dados_ata_cabecalho_tipo_retificacao(
    ata_retificacao_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_retificacao_completa,
        usuario=None,
    )
    assert resultado['cabecalho']['tipo_ata'] == 'Retificação'


def test_gerar_dados_ata_devolucoes_ao_tesouro_apresentacao_vazia(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    assert resultado['devolucoes_ao_tesouro'] == []


def test_gerar_dados_ata_repasses_pendentes_e_lista(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    assert isinstance(resultado['repasses_pendentes'], list)


def test_gerar_dados_ata_presentes_tem_estrutura_correta(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=None,
    )
    presentes = resultado['presentes_na_ata']
    assert 'presentes_ata_membros' in presentes
    assert 'presentes_ata_nao_membros' in presentes
    assert 'presentes_ata_conselho_fiscal' in presentes


def test_gerar_dados_ata_retificacoes_passada_corretamente(
    ata_retificacao_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_retificacao_completa,
        usuario=None,
    )
    assert resultado['retificacoes'] == 'Correção de valor'


def test_gerar_dados_ata_usuario_passado_para_dados_texto(
    ata_completa, ata_prestacao_conta_2020_1, ata_fechamento_periodo_2020_1,
    ata_conta_associacao_cartao, ata_acao_associacao_ptrf,
):
    usuario_mock = object()
    resultado = gerar_dados_ata(
        prestacao_de_contas=ata_prestacao_conta_2020_1,
        ata=ata_completa,
        usuario=usuario_mock,
    )
    assert resultado['dados_texto_da_ata']['usuario'] is usuario_mock
