import json
from datetime import date

import pytest
from model_bakery import baker
from rest_framework import status
from django.urls import resolve
from urllib.parse import parse_qs, urlparse
from waffle.testutils import override_flag

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
        status='APROVADA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_c_dre1(periodo_2020_1, _unidade_c_dre_1_ceu, _associacao_c_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_c_dre_1,
        data_recebimento=date(2020, 1, 3),
        status='RECEBIDA'
    )


@pytest.fixture
def _prestacao_conta_2019_2_unidade_a_dre1(periodo_2019_2, _unidade_a_dre_1, _associacao_a_dre_1):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=_associacao_a_dre_1,
        data_recebimento=date(2019, 1, 1),
        status='APROVADA_RESSALVA'
    )


@pytest.fixture
def _prestacao_conta_2020_1_unidade_b_dre2(periodo_2020_1, _unidade_b_dre_2, _associacao_b_dre_2):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=_associacao_b_dre_2,
        data_recebimento=date(2020, 1, 2)
    )


@pytest.fixture
def flag_dre_pcs_paginacao_ativa(db):
    with override_flag("dre-pcs-paginacao", active=True):
        yield


@pytest.fixture
def url_prestacoes_list_paginada(
    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
    _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra (período)
    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra (DRE)
    _dre_01,
    periodo_2020_1,
):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    return (
        "/api/prestacoes-contas/"
        f"?associacao__unidade__dre__uuid={dre_uuid}"
        f"&periodo__uuid={periodo_uuid}"
    )


def test_api_list_prestacoes_conta_por_periodo_e_dre(jwt_authenticated_client_a,
                                                     _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                     _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                                     _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                     _dre_01,
                                                     periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid

    url = f'/api/prestacoes-contas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)
    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-01',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'APROVADA',
            'tecnico_responsavel': '',
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'unidade_tipo_unidade': 'EMEI',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_nome_unidade(jwt_authenticated_client_a,
                                                    _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                    _prestacao_conta_2020_1_unidade_c_dre1,  # Não entra
                                                    _prestacao_conta_2019_2_unidade_a_dre1,  # Entra
                                                    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                    _dre_01,
                                                    periodo_2020_1,
                                                    periodo_2019_2):
    url = f'/api/prestacoes-contas/?nome=andorinha'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Deve retornar dois registros
    assert len(result) == 2

    # O resultado deve incluir apenas associações com nome que inclui "andorinha"
    assert all([assoc['unidade_nome'].lower().find('andorinha') >= 0 for assoc in result])


def test_api_list_prestacoes_conta_por_nome_associacao(jwt_authenticated_client_a,
                                                       _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                                       _prestacao_conta_2020_1_unidade_c_dre1,  # Não entra
                                                       _prestacao_conta_2019_2_unidade_a_dre1,  # Entra
                                                       _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                       _dre_01,
                                                       periodo_2020_1,
                                                       periodo_2019_2):
    url = f'/api/prestacoes-contas/?nome=america'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Deve retornar dois registros
    assert len(result) == 2

    # O resultado deve incluir apenas as prestações de contas _prestacao_conta_2020_1_unidade_a_dre1 e _prestacao_conta_2019_2_unidade_a_dre1
    # Essas são as únicas que tem associações com nome que inclui "america"
    assert all([pc['uuid'] in [str(_prestacao_conta_2020_1_unidade_a_dre1.uuid), str(_prestacao_conta_2019_2_unidade_a_dre1.uuid)] for pc in result])



def test_api_list_prestacoes_conta_por_tipo_unidade(jwt_authenticated_client_a,
                                                    _prestacao_conta_2020_1_unidade_a_dre1,  # Não entra
                                                    _prestacao_conta_2020_1_unidade_c_dre1,  # Entra
                                                    _prestacao_conta_2019_2_unidade_a_dre1,  # Não Entra
                                                    _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                                    _dre_01,
                                                    periodo_2020_1,
                                                    periodo_2019_2):
    url = f'/api/prestacoes-contas/?associacao__unidade__tipo_unidade=CEU'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-03',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'RECEBIDA',
            'tecnico_responsavel': '',
            'unidade_eol': '000102',
            'unidade_nome': 'Codorna',
            'unidade_tipo_unidade': 'CEU',
            'uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


@pytest.fixture
def _tecnico_a_dre1(_dre_01):
    return baker.make(
        'TecnicoDre',
        dre=_dre_01,
        nome='José Testando',
        rf='271170',
    )


@pytest.fixture
def _atribuicao_unidade_a_dre1(_tecnico_a_dre1, _unidade_a_dre_1, periodo_2020_1):
    return baker.make(
        'Atribuicao',
        tecnico=_tecnico_a_dre1,
        unidade=_unidade_a_dre_1,
        periodo=periodo_2020_1,
    )


@pytest.fixture
def _tecnico_b_dre1(_dre_01):
    return baker.make(
        'TecnicoDre',
        dre=_dre_01,
        nome='Ana Testando',
        rf='271171',
    )


@pytest.fixture
def _atribuicao_unidade_c_dre1(_tecnico_b_dre1, _unidade_c_dre_1_ceu, periodo_2020_1):
    return baker.make(
        'Atribuicao',
        tecnico=_tecnico_b_dre1,
        unidade=_unidade_c_dre_1_ceu,
        periodo=periodo_2020_1,
    )


def test_api_list_prestacoes_conta_por_tecnico(jwt_authenticated_client_a,
                                               _tecnico_a_dre1,
                                               _tecnico_b_dre1,
                                               _atribuicao_unidade_a_dre1,
                                               _atribuicao_unidade_c_dre1,
                                               _prestacao_conta_2020_1_unidade_a_dre1,  # Entra
                                               _prestacao_conta_2020_1_unidade_c_dre1,  # Não entra
                                               _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                               _prestacao_conta_2020_1_unidade_b_dre2,  # Não entra
                                               _dre_01,
                                               periodo_2020_1):
    dre_uuid = _dre_01.uuid
    periodo_uuid = periodo_2020_1.uuid
    tecnico_uuid = _tecnico_a_dre1.uuid

    url = f'/api/prestacoes-contas/?associacao__unidade__dre__uuid={dre_uuid}&periodo__uuid={periodo_uuid}&tecnico={tecnico_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-01',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'APROVADA',
            'tecnico_responsavel': 'José Testando',
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'unidade_tipo_unidade': 'EMEI',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_data_recebimento(jwt_authenticated_client_a,
                                                        _prestacao_conta_2020_1_unidade_a_dre1,  # Não Entra
                                                        _prestacao_conta_2020_1_unidade_c_dre1,  # Não Entra
                                                        _prestacao_conta_2019_2_unidade_a_dre1,  # Não entra
                                                        _prestacao_conta_2020_1_unidade_b_dre2,  # Entra
                                                        _dre_01,
                                                        periodo_2020_1):
    url = f'/api/prestacoes-contas/?data_inicio=2020-01-02&data_fim=2020-01-02'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-02',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'NAO_APRESENTADA',
            'tecnico_responsavel': '',
            'unidade_eol': '000201',
            'unidade_nome': 'Bentivi',
            'unidade_tipo_unidade': 'EMEI',
            'uuid': f'{_prestacao_conta_2020_1_unidade_b_dre2.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_b_dre2.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_status_aprovada_e_aprovada_ressalva(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_c_dre1, # Não entra
    _prestacao_conta_2019_2_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_b_dre2, # Não entra
    _dre_01,
    periodo_2020_1,
    periodo_2019_2
):
    url = f'/api/prestacoes-contas/?status=APROVADA,APROVADA_RESSALVA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_api_list_prestacoes_conta_por_status_aprovada(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_c_dre1, # Não entra
    _prestacao_conta_2019_2_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_b_dre2, # Não entra
    _dre_01,
    periodo_2020_1,
    periodo_2019_2
):
    url = f'/api/prestacoes-contas/?status=APROVADA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-01',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'APROVADA',
            'tecnico_responsavel': '',
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'unidade_tipo_unidade': 'EMEI',
            'uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_a_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_status_aprovada_ressalva(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_c_dre1, # Não entra
    _prestacao_conta_2019_2_unidade_a_dre1, # Entra
    _prestacao_conta_2020_1_unidade_b_dre2, # Não entra
    _dre_01,
    periodo_2020_1,
    periodo_2019_2
):
    url = f'/api/prestacoes-contas/?status=APROVADA_RESSALVA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2019_2.uuid}',
            'data_recebimento': '2019-01-01',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'APROVADA_RESSALVA',
            'tecnico_responsavel': '',
            'unidade_eol': '000101',
            'unidade_nome': 'Andorinha',
            'unidade_tipo_unidade': 'EMEI',
            'uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2019_2_unidade_a_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'

        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_prestacoes_conta_por_status_recebida(
    jwt_authenticated_client_a,
    _prestacao_conta_2020_1_unidade_a_dre1, # Não entra
    _prestacao_conta_2020_1_unidade_c_dre1, # Entra
    _prestacao_conta_2019_2_unidade_a_dre1, # Não entra
    _prestacao_conta_2020_1_unidade_b_dre2, # Não entra
    _dre_01,
    periodo_2020_1,
    periodo_2019_2
):
    url = f'/api/prestacoes-contas/?status=RECEBIDA'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = [
        {
            'periodo_uuid': f'{periodo_2020_1.uuid}',
            'data_recebimento': '2020-01-03',
            'data_ultima_analise': None,
            'processo_sei': '',
            'status': 'RECEBIDA',
            'tecnico_responsavel': '',
            'unidade_eol': '000102',
            'unidade_nome': 'Codorna',
            'unidade_tipo_unidade': 'CEU',
            'uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.uuid}',
            'associacao_uuid': f'{_prestacao_conta_2020_1_unidade_c_dre1.associacao.uuid}',
            'devolucao_ao_tesouro': 'Não'
        },

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado

def test_api_list_prestacoes_com_flag_paginacao_ativa(
    jwt_authenticated_client_a,
    flag_dre_pcs_paginacao_ativa,
    url_prestacoes_list_paginada,
    _prestacao_conta_2020_1_unidade_a_dre1,
):
    response = jwt_authenticated_client_a.get(
        url_prestacoes_list_paginada,
        content_type="application/json",
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Deve retornar a estrutura paginada
    assert isinstance(result, dict)
    assert {
        'links', 'count', 'page', 'page_size', 'total_pages', 'results'
    }.issubset(result.keys())

    # Apenas uma prestação pertence à DRE e período
    assert result["count"] == 1
    assert len(result["results"]) == 1

    # Deve retornar a prestação esperada
    assert result["results"][0]["uuid"] == str(
        _prestacao_conta_2020_1_unidade_a_dre1.uuid
    )

    assert result["links"]["next"] is None
    assert result["links"]["previous"] is None


def test_api_list_prestacoes_pagina_1_e_2(
    jwt_authenticated_client_a,
    flag_dre_pcs_paginacao_ativa,
    url_prestacoes_list_paginada,
    _prestacao_conta_2020_1_unidade_a_dre1,
    _prestacao_conta_2019_2_unidade_a_dre1,
    monkeypatch,
):
    # Remove o filtro de período para obter as duas
    # prestações existentes na mesma DRE.
    url = url_prestacoes_list_paginada.split(
        "&periodo__uuid="
    )[0]

    caminho = url.split("?")[0]
    view_class = resolve(caminho).func.cls

    # Configura temporariamente uma prestação por página
    monkeypatch.setattr(
        view_class.pagination_class,
        "page_size",
        1,
    )

    # Primeira página
    response_1 = jwt_authenticated_client_a.get(
        f"{url}&page=1",
        content_type="application/json",
    )

    result_1 = json.loads(response_1.content)

    assert response_1.status_code == status.HTTP_200_OK
    assert result_1["count"] == 2
    assert len(result_1["results"]) == 1
    assert result_1["links"]["previous"] is None
    assert result_1["links"]["next"] is not None

    # Deve apontar para a página 2
    parametros_next = parse_qs(
        urlparse(result_1["links"]["next"]).query
    )

    assert parametros_next["page"] == ["2"]

    # Deve preservar o filtro da DRE
    parametros_originais = parse_qs(
        urlparse(url).query
    )

    assert (
        parametros_next["associacao__unidade__dre__uuid"]
        == parametros_originais["associacao__unidade__dre__uuid"]
    )

    # Segunda página
    response_2 = jwt_authenticated_client_a.get(
        f"{url}&page=2",
        content_type="application/json",
    )

    result_2 = json.loads(response_2.content)

    assert response_2.status_code == status.HTTP_200_OK
    assert result_2["count"] == 2
    assert len(result_2["results"]) == 1
    assert result_2["links"]["next"] is None
    assert result_2["links"]["previous"] is not None

    # Não pode repetir o mesmo registro nas páginas
    uuid_pagina_1 = result_1["results"][0]["uuid"]
    uuid_pagina_2 = result_2["results"][0]["uuid"]

    assert uuid_pagina_1 != uuid_pagina_2

    # Deve retornar exatamente as duas prestações da DRE
    uuids_esperados = {
        str(_prestacao_conta_2020_1_unidade_a_dre1.uuid),
        str(_prestacao_conta_2019_2_unidade_a_dre1.uuid),
    }

    assert {
        uuid_pagina_1,
        uuid_pagina_2,
    } == uuids_esperados

