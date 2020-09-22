import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def _dre_01():
    return baker.make(
        'Unidade',
        codigo_eol='000001',
        tipo_unidade='DRE',
        nome='Dre1',
        sigla='D1'
    )


@pytest.fixture
def _dre_02():
    return baker.make(
        'Unidade',
        codigo_eol='000002',
        tipo_unidade='DRE',
        nome='Dre2',
        sigla='D2'
    )


@pytest.fixture
def _unidade_a_dre_1(_dre_01):
    return baker.make(
        'Unidade',
        codigo_eol="000101",
        tipo_unidade="EMEI",
        nome="Andorinha",
        sigla="",
        dre=_dre_01,
    )


@pytest.fixture
def _unidade_b_dre_2(_dre_02):
    return baker.make(
        'Unidade',
        codigo_eol="000201",
        tipo_unidade="EMEI",
        nome="Bentivi",
        sigla="",
        dre=_dre_02,
    )


@pytest.fixture
def _unidade_c_dre_1(_dre_01):
    return baker.make(
        'Unidade',
        codigo_eol="000102",
        tipo_unidade="EMEI",
        nome="Codorna",
        sigla="",
        dre=_dre_01,
    )


@pytest.fixture
def _associacao_a_dre_1(_unidade_a_dre_1, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='América',
        cnpj='52.302.275/0001-83',
        unidade=_unidade_a_dre_1,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _associacao_b_dre_2(_unidade_b_dre_2, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Bolivia',
        cnpj='23.034.742/0001-33',
        unidade=_unidade_b_dre_2,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _associacao_c_dre_1(_unidade_c_dre_1, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-71',
        unidade=_unidade_c_dre_1,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_a_dre1(periodo_2020_1, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_a_dre_1,
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_c_dre1(periodo_2020_1, _unidade_c_dre_1, _associacao_c_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_c_dre_1,
    )


@pytest.fixture
def _prestacao_conta_2019_2_unidade_a_dre1(periodo_2019_2, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=_associacao_a_dre_1,
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_b_dre2(periodo_2020_1, _unidade_b_dre_2, _associacao_b_dre_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_b_dre_2,
    )


def test_api_list_prestacoes_conta_por_periodo_e_dre(client,
                                                     _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                     _prestacao_conta_2020_1_unidade_c_dre1,  # Entra
                                                     _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                                     _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                     _dre_01,
                                                     periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'
        },
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000102',
            'unidade_nome': 'Codorna',
            'uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.associacao.uuid}'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_nome_unidade(client,
                                                    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                    _prestacao_conta_2020_1_unidade_c_dre1,  # Não entra
                                                    _prestacao_conta_2019_2_unidade_a_dre1,  # Entra
                                                    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                    _dre_01,
                                                    periodo_2020_1,
                                                    periodo_2019_2):
    url = f'/api/prestacoes-contas/?nome=andorinha'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'
        },
        {
            'periodo_uuid': f'{periodo_2019_2.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.associacao.uuid}'
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_nome_associacao(client,
                                                       _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                       _prestacao_conta_2020_1_unidade_c_dre1,  # Não entra
                                                       _prestacao_conta_2019_2_unidade_a_dre1,  # Entra
                                                       _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                       _dre_01,
                                                       periodo_2020_1,
                                                       periodo_2019_2):
    url = f'/api/prestacoes-contas/?nome=america'

    response = client.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'
        },
        {
            'periodo_uuid': f'{periodo_2019_2.uuid}',
            'data_recebimento': None,
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'DOCS_PENDENTES',
            'tecnico_responsavel': None,
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.associacao.uuid}'
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
