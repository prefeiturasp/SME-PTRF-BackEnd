import json
from datetime import date

import pytest
from model_bakery import baker
from rest_framework import status
from django.urls import resolve
from urllib.parse import parse_qs, urlparse

pytestmark = pytest.mark.django_db


@pytest.fixture
def _dre_01_todos_os_status():
    return baker.make(
        'Unidade',
        codigo_eol='000001',
        tipo_unidade='DRE',
        nome='Dre1',
        sigla='D1'
    )


@pytest.fixture
def _dre_02_todos_os_status():
    return baker.make(
        'Unidade',
        codigo_eol='000002',
        tipo_unidade='DRE',
        nome='Dre2',
        sigla='D2'
    )


@pytest.fixture
def _unidade_a_dre_1_todos_os_status(_dre_01_todos_os_status):
    return baker.make(
        'Unidade',
        codigo_eol="000101",
        tipo_unidade="EMEI",
        nome="Andorinha",
        sigla="",
        dre=_dre_01_todos_os_status,
    )


@pytest.fixture
def _unidade_b_dre_2_todos_os_status(_dre_02_todos_os_status):
    return baker.make(
        'Unidade',
        codigo_eol="000201",
        tipo_unidade="EMEI",
        nome="Bentivi",
        sigla="",
        dre=_dre_02_todos_os_status,
    )


@pytest.fixture
def _unidade_c_dre_1_ceu_todos_os_status(_dre_01_todos_os_status):
    return baker.make(
        'Unidade',
        codigo_eol="000102",
        tipo_unidade="CEU",
        nome="Codorna",
        sigla="",
        dre=_dre_01_todos_os_status,
    )


@pytest.fixture
def _associacao_a_dre_1_todos_os_status(_unidade_a_dre_1_todos_os_status, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='América',
        cnpj='52.302.275/0001-83',
        unidade=_unidade_a_dre_1_todos_os_status,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _associacao_b_dre_2_todos_os_status(_unidade_b_dre_2_todos_os_status, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Bolivia',
        cnpj='23.034.742/0001-33',
        unidade=_unidade_b_dre_2_todos_os_status,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _associacao_c_dre_1_todos_os_status(_unidade_c_dre_1_ceu_todos_os_status, periodo_2020_1, periodo_2019_2):
    return baker.make(
        'Associacao',
        nome='Cuba',
        cnpj='88.102.703/0001-71',
        unidade=_unidade_c_dre_1_ceu_todos_os_status,
        periodo_inicial=periodo_2019_2
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status(periodo_2020_1, _unidade_a_dre_1_todos_os_status,
                                                           _associacao_a_dre_1_todos_os_status):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_a_dre_1_todos_os_status,
        data_recebimento=date(2020, 1, 1),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_c_dre1_todos_os_status(periodo_2020_1, _unidade_c_dre_1_ceu_todos_os_status,
                                                           _associacao_c_dre_1_todos_os_status):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_c_dre_1_todos_os_status,
        data_recebimento=date(2020, 1, 3),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status(periodo_2019_2, _unidade_a_dre_1_todos_os_status,
                                                           _associacao_a_dre_1_todos_os_status):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=_associacao_a_dre_1_todos_os_status,
        data_recebimento=date(2019, 1, 1),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status(periodo_2020_1, _unidade_b_dre_2_todos_os_status,
                                                           _associacao_b_dre_2_todos_os_status):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_b_dre_2_todos_os_status,
        data_recebimento=date(2020, 1, 2),
        status='NAO_RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_a_dre1_em_analise(periodo_2020_1, _unidade_a_dre_1_todos_os_status,
                                                      _associacao_a_dre_1_todos_os_status):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_a_dre_1_todos_os_status,
        data_recebimento=date(2020, 1, 1),
        status='EM_ANALISE'
    )


@pytest.fixture
def flag_dre_pcs_paginacao_ativa(flag_factory):
    flag_factory.create(
        name='dre-pcs-paginacao',
        everyone=True,
    )

@pytest.fixture
def url_prestacoes_todos_os_status(
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status,  # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status,  # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status,  # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status,  # Entra como NAO_APRESENTADA
    periodo_2020_1,
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    return (
        "/api/prestacoes-contas/todos-os-status/"
        f"?associacao__unidade__dre__uuid={dre_uuid}"
        f"&periodo__uuid={periodo_uuid}"
    )


def test_api_list_prestacoes_conta_todos_os_status_por_periodo_e_dre(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # nenhum dos registros deve ser de un período diferente de periodo_uuid
    assert all([r['periodo_uuid'] == str(periodo_uuid) for r in result])

    # nenhum dos registros deve ser de uma dre diferente de dre_uuid
    assert all([r['associacao_uuid'] in [str(_associacao_c_dre_1_todos_os_status.uuid), str(_prestacao_conta_2020_1_unidade_a_dre1_todos_os_status.associacao.uuid)] for r in result])


def test_api_list_prestacoes_conta_todos_os_status_por_periodo_e_dre_inclui_outros_status(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_em_analise, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    _associacao_a_dre_1_todos_os_status, # Entra como EM_ANALISE
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # Não deve retornat status diferentes de NAO_APRESENTADA e NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_APRESENTADA', 'EM_ANALISE'] for pc in result)


def test_api_list_prestacoes_conta_todos_os_status_por_nome_unidade(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=andorinha'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1_todos_os_status.associacao.uuid}'

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=codorna'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_associacao_c_dre_1_todos_os_status.uuid}'


def test_api_list_prestacoes_conta_todos_os_status_por_nome_associacao(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=america'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1_todos_os_status.associacao.uuid}'

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&nome=cuba'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_associacao_c_dre_1_todos_os_status.uuid}'


def test_api_list_prestacoes_conta_todos_os_status_por_tipo_unidade(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&tipo_unidade=EMEI'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Deve retornar a PC da associação correta
    assert result[0]['associacao_uuid'] == f'{_prestacao_conta_2020_1_unidade_a_dre1_todos_os_status.associacao.uuid}'


def test_api_list_prestacoes_conta_todos_os_status_por_status_nao_apresentada(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_APRESENTADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Não deve retornat status diferentes de NAO_APRESENTADA
    assert all(pc['status'] in ['NAO_APRESENTADA'] for pc in result)


def test_api_list_prestacoes_conta_todos_os_status_nao_recebida(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_RECEBIDA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar um registro
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1

    # Não deve retornat status diferentes de NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_RECEBIDA'] for pc in result)


def test_api_list_prestacoes_conta_todos_os_status_nao_recebida_nao_apresentada(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=NAO_RECEBIDA,NAO_APRESENTADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # Não deve retornat status diferentes de NAO_APRESENTADA e NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_APRESENTADA', 'NAO_RECEBIDA'] for pc in result)


def test_api_list_prestacoes_conta_todos_os_status_sem_filtro_por_status(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    # Deve retornar dois registros
    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

    # Não deve retornat status diferentes de NAO_APRESENTADA e NAO_RECEBIDA
    assert all(pc['status'] in ['NAO_APRESENTADA', 'NAO_RECEBIDA'] for pc in result)


def test_api_list_prestacoes_conta_todos_os_status_por_status_invalido(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1_todos_os_status, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1_todos_os_status, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2_todos_os_status, # Não entra
    _dre_01_todos_os_status,
    _associacao_c_dre_1_todos_os_status, # Entra como NAO_APRESENTADA
    periodo_2020_1
):
    dre_uuid = _dre_01_todos_os_status.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/todos-os-status/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&status=TODOS'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
        'erro': 'status-invalido',
        'operacao': 'todos-os-status',
        'mensagem': 'Passe um status de prestação de contas válido.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado


def test_api_list_prestacoes_todos_os_status_com_flag_paginacao_ativa(
    jwt_authenticated_client_a,
    flag_dre_pcs_paginacao_ativa,
    url_prestacoes_todos_os_status,
):
    response = jwt_authenticated_client_a.get(
        url_prestacoes_todos_os_status,
        content_type="application/json",
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Deve retornar a estrutura paginada do DRF
    assert isinstance(result, dict)
    assert {
        'links', 'count', 'page', 'page_size', 'total_pages', 'results'
    }.issubset(result.keys())

    # Deve encontrar os dois registros da DRE e período informados
    assert result["count"] == 2
    assert isinstance(result["results"], list)
    assert len(result["results"]) == 2

    # Deve incluir a prestação de contas não apresentada
    assert any(
        pc["status"] == "NAO_APRESENTADA"
        for pc in result["results"]
    )

    # Não há páginas adicionais quando os dois registros
    # cabem na mesma página
    assert result["links"]["next"] is None
    assert result["links"]["previous"] is None


def test_api_list_prestacoes_todos_os_status_pagina_1_e_2(
    jwt_authenticated_client_a,
    flag_dre_pcs_paginacao_ativa,
    url_prestacoes_todos_os_status,
    monkeypatch,
):
    # Configura temporariamente a paginação para
    # retornar apenas um registro por página
    caminho = url_prestacoes_todos_os_status.split("?")[0]

    view_class = resolve(caminho).func.cls

    monkeypatch.setattr(
        view_class.pagination_class,
        "page_size",
        1,
    )

    # Primeira página
    response_1 = jwt_authenticated_client_a.get(
        f"{url_prestacoes_todos_os_status}&page=1",
        content_type="application/json",
    )

    result_1 = json.loads(response_1.content)

    assert response_1.status_code == status.HTTP_200_OK
    assert result_1["count"] == 2
    assert len(result_1["results"]) == 1
    assert result_1["links"]["previous"] is None
    assert result_1["links"]["next"] is not None

    # O link next deve apontar para a página 2
    parametros_next = parse_qs(
        urlparse(result_1["links"]["next"]).query
    )

    assert parametros_next["page"] == ["2"]

    # Os filtros devem ser preservados no link
    parametros_originais = parse_qs(
        urlparse(url_prestacoes_todos_os_status).query
    )

    assert (
        parametros_next["associacao__unidade__dre__uuid"]
        == parametros_originais["associacao__unidade__dre__uuid"]
    )

    assert (
        parametros_next["periodo__uuid"]
        == parametros_originais["periodo__uuid"]
    )

    # Segunda página
    response_2 = jwt_authenticated_client_a.get(
        f"{url_prestacoes_todos_os_status}&page=2",
        content_type="application/json",
    )

    result_2 = json.loads(response_2.content)

    assert response_2.status_code == status.HTTP_200_OK
    assert result_2["count"] == 2
    assert len(result_2["results"]) == 1
    assert result_2["links"]["next"] is None
    assert result_2["links"]["previous"] is not None

    # Não deve retornar o mesmo registro nas duas páginas
    assert result_1["results"][0] != result_2["results"][0]

    # Os registros das duas páginas devem incluir
    # a prestação de contas não apresentada
    registros = result_1["results"] + result_2["results"]

    assert any(
        pc["status"] == "NAO_APRESENTADA"
        for pc in registros
    )
