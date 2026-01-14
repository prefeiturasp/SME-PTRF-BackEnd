import uuid
import pytest
import json
from unittest.mock import patch

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
def test_list_default_prioridade_paa_relatorio(jwt_authenticated_client_sme, flag_paa):
    response = jwt_authenticated_client_sme.get("/api/prioridades-paa-relatorio/")
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "results" in result
    assert len(result["results"]) == 0
    assert "count" in result
    assert result["count"] == 0
    assert "links" not in result


@pytest.mark.django_db
def test_list_ordenacao_customizada_prioridade_paa(
        jwt_authenticated_client_sme, flag_paa, paa, programa_pdde, acao_pdde, acao_associacao, outro_recurso):

    # Deve estar no ranking 5
    item1 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None
    )
    # Deve estar no ranking 6
    item2 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_associacao=None,
        acao_pdde=acao_pdde,
        programa_pdde=programa_pdde
    )
    # Deve estar no ranking 7
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
    # Deve estar no ranking 4
    itemOutroRecurso = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name,
        outro_recurso=outro_recurso,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None
    )
    response = jwt_authenticated_client_sme.get("/api/prioridades-paa/")
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 7
    assert 'count' in result
    assert result['count'] == 7
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None

    assert result['results'][0]['uuid'] == str(item4.uuid)

    assert result['results'][1]['uuid'] == str(item5.uuid)

    assert result['results'][2]['uuid'] == str(item6.uuid)

    assert result['results'][3]['uuid'] == str(itemOutroRecurso.uuid)

    assert result['results'][4]['uuid'] == str(item1.uuid)

    assert result['results'][5]['uuid'] == str(item2.uuid)

    assert result['results'][6]['uuid'] == str(item3.uuid)

    


@pytest.mark.django_db
def test_list_ordenacao_customizada_prioridade_paa_relatorio(
    jwt_authenticated_client_sme, flag_paa, paa, programa_pdde, acao_pdde, acao_associacao
):
    item1 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None,
    )
    item2 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_associacao=None,
        acao_pdde=acao_pdde,
        programa_pdde=programa_pdde,
    )
    item3 = PrioridadePaaFactory(
        paa=paa,
        prioridade=0,
        recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None,
    )
    item4 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.PTRF.name,
        acao_associacao=acao_associacao,
        acao_pdde=None,
    )
    item5 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.PDDE.name,
        acao_associacao=None,
        acao_pdde=acao_pdde,
        programa_pdde=programa_pdde,
    )
    item6 = PrioridadePaaFactory(
        paa=paa,
        prioridade=1,
        recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        acao_associacao=None,
        acao_pdde=None,
        programa_pdde=None,
    )

    response = jwt_authenticated_client_sme.get("/api/prioridades-paa-relatorio/")
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "results" in result
    assert len(result["results"]) == 6
    assert "count" in result
    assert result["count"] == 6
    assert "links" not in result

    assert result["results"][0]["uuid"] == str(item4.uuid)
    assert result["results"][1]["uuid"] == str(item5.uuid)
    assert result["results"][2]["uuid"] == str(item6.uuid)
    assert result["results"][3]["uuid"] == str(item1.uuid)
    assert result["results"][4]["uuid"] == str(item2.uuid)
    assert result["results"][5]["uuid"] == str(item3.uuid)


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
    # campos requeridos quando é PTRF/CAPITAL
    assert result.keys() == {'especificacao_material'}


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
def test_cria_prioridade_paa_outro_recurso(jwt_authenticated_client_sme, flag_paa,
                                           paa, especificacao_material):
    data = {
        "paa": str(paa.uuid),
        "prioridade": 1,
        "recurso": "OUTRO_RECURSO",
        "tipo_aplicacao": "CAPITAL",
        "especificacao_material": str(especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/", data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['outro_recurso'] == ["Outro Recurso não informada quando o tipo de Recurso é OUTRO_RECURSO."]
    assert result.keys() == {'outro_recurso'}


@pytest.mark.django_db
@patch('sme_ptrf_apps.paa.services.resumo_prioridades_service.ResumoPrioridadesService.resumo_prioridades')
def test_cria_prioridade_paa_recurso_proprio_capital(mock_resumo, jwt_authenticated_client_sme, flag_paa,
                                                     paa, especificacao_material):
    # Mock do resumo de prioridades para Recursos Próprios
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            'children': [
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_receita',
                    'recurso': 'Receita',
                    'custeio': 0,
                    'capital': 0,
                    'livre_aplicacao': 0
                },
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_despesas',
                    'recurso': 'Despesas previstas',
                    'custeio': 0,
                    'capital': 0,
                    'livre_aplicacao': 0
                },
                {
                    'key': f'{RecursoOpcoesEnum.RECURSO_PROPRIO.name}_saldo',
                    'recurso': 'Saldo',
                    'custeio': 0,
                    'capital': 0,
                    'livre_aplicacao': 20
                }
            ]
        }
    ]

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
        'outro_recurso',
        'programa_pdde',
        'acao_pdde',
        'tipo_aplicacao',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total',
        'copia_de'
    }
    assert PrioridadePaa.objects.count() == 1


@pytest.mark.django_db
@patch('sme_ptrf_apps.paa.services.resumo_prioridades_service.ResumoPrioridadesService.resumo_prioridades')
def test_altera_prioridade_custeio_para_capital_com_sucesso(mock_resumo, jwt_authenticated_client_sme,
                                                            flag_paa, prioridade_paa_ptrf_custeio):
    # Mock do resumo de prioridades para PTRF
    mock_resumo.return_value = [
        {
            'key': RecursoOpcoesEnum.PTRF.name,
            'children': [
                {
                    'key': str(prioridade_paa_ptrf_custeio.acao_associacao.uuid),
                    'children': [
                        {
                            'key': f'{str(prioridade_paa_ptrf_custeio.acao_associacao.uuid)}_receita',
                            'recurso': 'Receita',
                            'custeio': 1000.00,
                            'capital': 1000.00,
                            'livre_aplicacao': 500.00
                        },
                        {
                            'key': f'{str(prioridade_paa_ptrf_custeio.acao_associacao.uuid)}_despesa',
                            'recurso': 'Despesas previstas',
                            'custeio': 100.00,
                            'capital': 50.00,
                            'livre_aplicacao': 0
                        },
                        {
                            'key': f'{str(prioridade_paa_ptrf_custeio.acao_associacao.uuid)}_saldo',
                            'recurso': 'Saldo',
                            'custeio': 100.00,
                            'capital': 50.00,
                            'livre_aplicacao': 0
                        },

                    ]
                }
            ]
        }
    ]

    prioridade_paa = prioridade_paa_ptrf_custeio
    payload = {
        "paa": str(prioridade_paa.paa.uuid),
        "prioridade": SimNaoChoices.NAO,
        "recurso": RecursoOpcoesEnum.PTRF.name,
        "acao_associacao": str(prioridade_paa.acao_associacao.uuid),
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CAPITAL.name,
        "especificacao_material": str(prioridade_paa.especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.patch(f"/api/prioridades-paa/{prioridade_paa.uuid}/", payload)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert result['tipo_despesa_custeio'] is None
    # campos retornados
    assert result.keys() == {
        'uuid',
        'paa',
        'prioridade',
        'recurso',
        'acao_associacao',
        'outro_recurso',
        'programa_pdde',
        'acao_pdde',
        'tipo_aplicacao',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total',
        'copia_de'
    }


@pytest.mark.django_db
def test_altera_prioridade_ptrf_para_recursos_proprios_com_sucesso(jwt_authenticated_client_sme,
                                                                   flag_paa,
                                                                   prioridade_paa_ptrf_custeio):
    prioridade_paa = prioridade_paa_ptrf_custeio
    payload = {
        "paa": str(prioridade_paa.paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "tipo_despesa_custeio": str(prioridade_paa.tipo_despesa_custeio.uuid),
        "especificacao_material": str(prioridade_paa.especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.patch(f"/api/prioridades-paa/{prioridade_paa.uuid}/", payload)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert result['acao_associacao'] is None
    assert result['acao_pdde'] is None
    assert result['programa_pdde'] is None
    # campos retornados
    assert result.keys() == {
        'uuid',
        'paa',
        'prioridade',
        'recurso',
        'acao_associacao',
        'outro_recurso',
        'programa_pdde',
        'acao_pdde',
        'tipo_aplicacao',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total',
        'copia_de'
    }


@pytest.mark.django_db
def test_altera_prioridade_ptrf_para_recursos_proprios_exige_tipo_despesa_custeio(jwt_authenticated_client_sme,
                                                                                  flag_paa,
                                                                                  prioridade_paa_ptrf_custeio):
    prioridade_paa = prioridade_paa_ptrf_custeio
    payload = {
        "paa": str(prioridade_paa.paa.uuid),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "especificacao_material": str(prioridade_paa.especificacao_material.uuid),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.patch(f"/api/prioridades-paa/{prioridade_paa.uuid}/", payload)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # campos retornados
    assert result.keys() == {
        'tipo_despesa_custeio',
    }

    assert result['tipo_despesa_custeio'] == ["Tipo de despesa não informado quando o tipo de aplicação é Custeio."]

    assert PrioridadePaa.objects.count() == 1


@pytest.mark.django_db
def test_altera_prioridade_nao_encontrada(jwt_authenticated_client_sme, flag_paa):
    payload = {
        "paa": str(uuid.uuid4()),
        "prioridade": SimNaoChoices.SIM,
        "recurso": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
        "tipo_aplicacao": TipoAplicacaoOpcoesEnum.CUSTEIO.name,
        "especificacao_material": str(uuid.uuid4()),
        "valor_total": 20
    }
    response = jwt_authenticated_client_sme.patch(f"/api/prioridades-paa/{uuid.uuid4()}/", payload)
    result = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # campos retornados
    assert result.keys() == {'mensagem'}

    assert result['mensagem'] == "Prioridade não encontrada ou já foi removida da base de dados."


@pytest.mark.django_db
def test_delete_prioridade_com_sucesso(jwt_authenticated_client_sme, flag_paa, prioridade_paa_ptrf_custeio):
    assert PrioridadePaa.objects.count() == 1
    response = jwt_authenticated_client_sme.delete(f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert PrioridadePaa.objects.count() == 0

    response = jwt_authenticated_client_sme.get(f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = jwt_authenticated_client_sme.delete(f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_prioridade_nao_encontrada(jwt_authenticated_client_sme, flag_paa, prioridade_paa_ptrf_custeio):
    assert PrioridadePaa.objects.count() == 1
    response = jwt_authenticated_client_sme.delete(f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert PrioridadePaa.objects.count() == 0

    response = jwt_authenticated_client_sme.delete(f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_prioridade_em_lote_com_ressalvas(jwt_authenticated_client_sme, flag_paa, prioridade_paa_ptrf_custeio):
    assert PrioridadePaa.objects.count() == 1
    payload = {
        "lista_uuids": [
            str(prioridade_paa_ptrf_custeio.uuid),
            "03cbb3c7-10e8-4bdf-bdfa-b97864054c75"
        ]
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/excluir-lote/",
                                                 data=json.dumps(payload),
                                                 content_type='application/json')
    result = response.json()
    assert response.status_code == status.HTTP_200_OK, result
    assert result['erros'] == [{
        'erro': 'Objeto não encontrado.',
        'mensagem': 'O objeto Prioridade 03cbb3c7-10e8-4bdf-bdfa-b97864054c75 não foi encontrado na base de dados.'
    }]
    assert result['mensagem'] == 'Alguma das prioridades selecionadas já foi removida.'


@pytest.mark.django_db
def test_delete_prioridade_em_lote_sem_ressalvas(jwt_authenticated_client_sme, flag_paa, prioridade_paa_ptrf_custeio):
    assert PrioridadePaa.objects.count() == 1
    payload = {
        "lista_uuids": [
            str(prioridade_paa_ptrf_custeio.uuid),
        ]
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/excluir-lote/",
                                                 data=json.dumps(payload),
                                                 content_type='application/json')
    result = response.json()
    assert response.status_code == status.HTTP_200_OK, result
    assert result['erros'] == []
    assert result['mensagem'] == 'Prioridades removidas com sucesso.'


@pytest.mark.django_db
def test_delete_prioridade_em_lote_sem_lista_uuids(jwt_authenticated_client_sme, flag_paa):
    payload = {}
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/excluir-lote/",
                                                 data=json.dumps(payload),
                                                 content_type='application/json')
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Falta de informações'
    assert result['mensagem'] == 'É necessário enviar a lista de uuids a serem excluídos (lista_uuids).'


@pytest.mark.django_db
def test_delete_prioridade_em_lote_com_excecao(jwt_authenticated_client_sme, flag_paa):
    payload = {
        "lista_uuids": [
            "001000"  # uuid inválido
        ]
    }
    response = jwt_authenticated_client_sme.post("/api/prioridades-paa/excluir-lote/",
                                                 data=json.dumps(payload),
                                                 content_type='application/json')
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == "Falha ao excluir Prioridades em lote"


@pytest.mark.django_db
def test_duplicar_prioridade(jwt_authenticated_client_sme, flag_paa, prioridade_paa_ptrf_custeio):
    assert PrioridadePaa.objects.count() == 1
    response = jwt_authenticated_client_sme.post(
        f"/api/prioridades-paa/{prioridade_paa_ptrf_custeio.uuid}/duplicar/")

    result = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert result['uuid'] != str(prioridade_paa_ptrf_custeio.uuid)
    assert result['paa'] == str(prioridade_paa_ptrf_custeio.paa.uuid)
    assert result['prioridade'] == int(prioridade_paa_ptrf_custeio.prioridade)
    assert result['recurso'] == prioridade_paa_ptrf_custeio.recurso
    assert result['acao_associacao'] == str(prioridade_paa_ptrf_custeio.acao_associacao.uuid)

    # Não considera uuid, pois a factory prioridade_paa_ptrf_custeio não é recurso PDDE
    assert result['programa_pdde'] == prioridade_paa_ptrf_custeio.programa_pdde
    assert result['acao_pdde'] == prioridade_paa_ptrf_custeio.acao_pdde

    assert result['outro_recurso'] == prioridade_paa_ptrf_custeio.outro_recurso

    assert result['tipo_aplicacao'] == prioridade_paa_ptrf_custeio.tipo_aplicacao
    assert result['tipo_despesa_custeio'] == str(prioridade_paa_ptrf_custeio.tipo_despesa_custeio.uuid)
    assert result['especificacao_material'] == str(prioridade_paa_ptrf_custeio.especificacao_material.uuid)
    assert result['valor_total'] is None

    # contem a factory original e a duplicada
    assert PrioridadePaa.objects.count() == 2
