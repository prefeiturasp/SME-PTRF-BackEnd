import json
from datetime import date

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
def _unidade_c_dre_1_ceu(_dre_01):
    return baker.make(
        'Unidade',
        codigo_eol="000102",
        tipo_unidade="CEU",
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
def _associacao_c_dre_1(_unidade_c_dre_1_ceu, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-71',
        unidade=_unidade_c_dre_1_ceu,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_a_dre1(periodo_2020_1, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_a_dre_1,
        data_recebimento=date(2020, 1, 1),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_c_dre1(periodo_2020_1, _unidade_c_dre_1_ceu, _associacao_c_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_c_dre_1,
        data_recebimento=date(2020, 1, 3),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2019_2_unidade_a_dre1(periodo_2019_2, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=_associacao_a_dre_1,
        data_recebimento=date(2019, 1, 1),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_b_dre2(periodo_2020_1, _unidade_b_dre_2, _associacao_b_dre_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_b_dre_2,
        data_recebimento=date(2020, 1, 2),
        status='NAO_RECEBIDA'
    )


def test_api_list_prestacoes_conta_nao_recebidas_por_periodo_e_dre_sem_filtro_por_status(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
    _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
    _dre_01,
    _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    """ Deve listar todas as PC Não apresentadas ou Não recebidas """

    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # Não deve retornat status diferentes de NAO_APRESENTADA e NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_APRESENTADA', 'NAO_RECEBIDA'] for pc in result)


@pytest.fixture
def _prestacao_conta_2020_1_unidade_a_dre1_em_analise(periodo_2020_1, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_a_dre_1,
        data_recebimento=date(2020, 1, 1),
        status='EM_ANALISE'
    )


def test_api_list_prestacoes_conta_nao_recebidas_por_periodo_e_dre_nao_inclui_outros_status(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_em_analise, # Não Entra
    _prestacao_conta_2019_2_unidade_a_dre1, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2, # Não entra
    _dre_01,
    _associacao_c_dre_1, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    """ PCs de status diferente de Não Recebida devem ser ignoradas """

    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Não deve retornat status diferentes de NAO_APRESENTADA
    assert all(pc['status'] in ['NAO_APRESENTADA'] for pc in result)


def test_api_list_prestacoes_conta_nao_recebidas_por_nome_unidade(jwt_authenticated_client_a,
                                                                  _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                                  _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                                                  _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                                  _dre_01,
                                                                  _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
                                                                  periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=andorinha'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'


    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=codorna'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_associacao_c_dre_1.uuid}'


def test_api_list_prestacoes_conta_nao_recebidas_por_nome_associacao(jwt_authenticated_client_a,
                                                                     _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                                     _prestacao_conta_2019_2_unidade_a_dre1,
                                                                     # Não entra
                                                                     _prestacao_conta_2020_1_unidade_b_dre2,
                                                                     # Não entra
                                                                     _dre_01,
                                                                     _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
                                                                     periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=america'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'


    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=cuba'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_associacao_c_dre_1.uuid}'


def test_api_list_prestacoes_conta_nao_recebidas_por_tipo_unidade(jwt_authenticated_client_a,
                                                                  _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                                  _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                                                  _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                                  _dre_01,
                                                                  _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
                                                                  periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&tipo_unidade=EMEI'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}'


    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&tipo_unidade=CEU'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_associacao_c_dre_1.uuid}'



def test_api_list_prestacoes_conta_nao_recebidas_por_status_nao_recebida(jwt_authenticated_client_a,
                                                                         _prestacao_conta_2020_1_unidade_a_dre1,
                                                                         # Entra
                                                                         _prestacao_conta_2019_2_unidade_a_dre1,
                                                                         # Não entra
                                                                         _prestacao_conta_2020_1_unidade_b_dre2,
                                                                         # Não entra
                                                                         _dre_01,
                                                                         _associacao_c_dre_1,
                                                                         # Entra como NAO_APRESENTADA
                                                                         periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_RECEBIDA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Não deve retornat status diferentes de NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_RECEBIDA'] for pc in result)


def test_api_list_prestacoes_conta_nao_recebidas_por_status_nao_apresentada(jwt_authenticated_client_a,
                                                                            _prestacao_conta_2020_1_unidade_a_dre1,
                                                                            # Entra
                                                                            _prestacao_conta_2019_2_unidade_a_dre1,
                                                                            # Não entra
                                                                            _prestacao_conta_2020_1_unidade_b_dre2,
                                                                            # Não entra
                                                                            _dre_01,
                                                                            _associacao_c_dre_1,
                                                                            # Entra como NAO_APRESENTADA
                                                                            periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_APRESENTADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Não deve retornat status diferentes de NAO_APRESENTADA
    assert all(pc['status'] in ['NAO_APRESENTADA'] for pc in result)


def test_api_list_prestacoes_conta_nao_recebidas_por_status_diferente_nao_recebida_nao_apresentada(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
    _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
    _dre_01,
    _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
    periodo_2020_1):

    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=APROVADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'status-invalido',
        'mensagem': 'Esse endpoint só aceita o filtro por status para os status NAO_APRESENTADA e NAO_RECEBIDA.',
        'operacao': 'nao-recebidas'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_list_prestacoes_conta_nao_recebidas_por_mais_de_um_status(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
    _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
    _dre_01,
    _associacao_c_dre_1,  # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/nao-recebidas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_RECEBIDA,NAO_APRESENTADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # Não deve retornat status diferentes de NAO_APRESENTADA e NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_APRESENTADA', 'NAO_RECEBIDA'] for pc in result)
