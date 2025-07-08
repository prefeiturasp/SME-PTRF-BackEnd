import pytest
from rest_framework import status
from sme_ptrf_apps.paa.models.prioridade_paa import PrioridadePaa, SimNaoChoices
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.fixtures.factories import PrioridadePaaFactory


@pytest.mark.django_db
def test_list_default_prioridade_paa(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get("/api/prioridades-paa/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 0
    assert 'count' in result
    assert result['count'] == 0
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_ordenacao_customizada_prioridade_paa(
        jwt_authenticated_client_sme, flag_paa, paa, programa_pdde, acao_pdde, acao_associacao):

    # Deve estar no ranking 4
    item1 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None
    )
    # Deve estar no ranking 5
    item2 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_associacao=None,
        acao_pdde=acao_pdde,
        programa_pdde=programa_pdde
    )
    # Deve estar no ranking 6
    item3 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None
    )
    # Deve estar no ranking 1
    item4 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None
    )
    # Deve estar no ranking 2
    item5 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_associacao=None,
        acao_pdde=acao_pdde,
        programa_pdde=programa_pdde
    )
    # Deve estar no ranking 3
    item6 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None
    )
    response = jwt_authenticated_client_sme.get("/api/prioridades-paa/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 6
    assert 'count' in result
    assert result['count'] == 6
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None

    # Item 4 deve estar no ranking 1
    assert result['results'][0]['uuid'] == str(item4.uuid)

    # Item 5 deve estar no ranking 2
    assert result['results'][1]['uuid'] == str(item5.uuid)

    # Item 6 deve estar no ranking 3
    assert result['results'][2]['uuid'] == str(item6.uuid)

    # Item 1 deve estar no ranking 4
    assert result['results'][3]['uuid'] == str(item1.uuid)

    # Item 2 deve estar no ranking 5
    assert result['results'][4]['uuid'] == str(item2.uuid)

    # Item 3 deve estar no ranking 6
    assert result['results'][5]['uuid'] == str(item3.uuid)


@pytest.mark.django_db
def test_list_tabelas_endpoint(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get("/api/prioridades-paa/tabelas/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert result['prioridades'] == SimNaoChoices.to_dict()
    assert result['recursos'] == RecursoOpcoesEnum.to_dict()
    assert result['tipos_aplicacao'] == TipoAplicacaoOpcoesEnum.to_dict()


@pytest.mark.django_db
def test_cria_prioridade_paa_ptrf_capital(jwt_authenticated_client_sme, flag_paa, paa):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "PTRF",
        "tipo_aplicacao": "CAPITAL"
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['especificacao_material'] == ["Especificação de material/serviço não foi informada."]
    assert result['valor_total'] == ["O valor total não foi informado."]
    # campos requeridos quando é PTRF/CAPITAL
    assert result.keys() == {'especificacao_material', 'valor_total'}


@pytest.mark.django_db
def test_cria_prioridade_paa_ptrf_custeio(jwt_authenticated_client_sme, flag_paa,
                                          paa, especificacao_material):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "PTRF",
        "tipo_aplicacao": "CUSTEIO",
        "especificacao_material": str(especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['acao_associacao'] == ["Ação de Associação não informada quando o tipo de Recurso é PTRF."]
    # campos requeridos quando é PTRF/CUSTEIO
    assert result.keys() == {'acao_associacao'}


@pytest.mark.django_db
def test_cria_prioridade_paa_pdde_capital_sem_programa(jwt_authenticated_client_sme, flag_paa,
                                                       paa, especificacao_material):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "PDDE",
        "tipo_aplicacao": "CAPITAL",
        "especificacao_material": str(especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    assert result['programa_pdde'] == ["Programa PDDE não foi informado quando o tipo de Recurso é PDDE."]
    # campos requeridos quando é PDDE/CAPITAL
    assert result.keys() == {'programa_pdde'}


@pytest.mark.django_db
def test_cria_prioridade_paa_pdde_capital_sem_acao_pdde(jwt_authenticated_client_sme, flag_paa,
                                                        paa, especificacao_material, programa_pdde):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "PDDE",
        "tipo_aplicacao": "CAPITAL",
        "especificacao_material": str(especificacao_material.uuid),
        "programa_pdde": str(programa_pdde.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    assert result['acao_pdde'] == ["Ação PDDE não foi informado quando o tipo de Recurso é PDDE."]
    # campos requeridos quando é PDDE/CAPITAL
    assert result.keys() == {'acao_pdde'}


@pytest.mark.django_db
def test_cria_prioridade_paa_pdde_custeio(jwt_authenticated_client_sme, flag_paa,
                                          paa, especificacao_material, programa_pdde, acao_pdde):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "PDDE",
        "tipo_aplicacao": "CUSTEIO",
        "especificacao_material": str(especificacao_material.uuid),
        "programa_pdde": str(programa_pdde.uuid),
        "acao_pdde": str(acao_pdde.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.content
    # campos requeridos quando é [QUALQUER RECURSO]/CUSTEIO
    assert result.keys() == {'tipo_despesa_custeio'}
    assert result['tipo_despesa_custeio'] == ["Tipo de despesa não informado quando o tipo de aplicação é Custeio."]


@pytest.mark.django_db
def test_cria_prioridade_paa_recurso_proprio_capital(jwt_authenticated_client_sme, flag_paa,
                                                     paa, especificacao_material):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "RECURSO_PROPRIO",
        "tipo_aplicacao": "CAPITAL",
        "especificacao_material": str(especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_201_CREATED, response.status_code
    assert result['paa'] == str(paa.uuid)
    assert result['prioridade'] == 1
    assert result['recurso'] == "RECURSO_PROPRIO"
    assert result['tipo_aplicacao'] == "CAPITAL"
    assert result['especificacao_material'] == str(especificacao_material.uuid)
    assert result['valor_total'] == '20.00'
    assert result['acao_associacao'] is None
    assert result['programa_pdde'] is None
    assert result['acao_pdde'] is None
    assert result['tipo_despesa_custeio'] is None
    assert result.keys() == {
        'uuid',
        'paa',
        'prioridade',
        'recurso',
        'acao_associacao',
        'programa_pdde',
        'acao_pdde',
        'tipo_aplicacao',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total'
    }
    assert PrioridadePaa.objects.count() == 1
