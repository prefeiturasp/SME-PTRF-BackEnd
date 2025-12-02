import pytest
from datetime import date
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_carrega_paas_anteriores(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):

    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    # considerar mesma associacao
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa_2025.uuid)}/paas-anteriores/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0]['periodo_paa_objeto']['referencia'] == "Periodo 2024"
    assert result[0]['associacao'] == str(paa_2024.associacao.uuid)


def test_action_resumo_prioridades(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):

    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2025 = paa_factory.create(periodo_paa=periodo_2025)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa_2025.uuid)}/resumo-prioridades/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 3
    assert result[0]['key'] == 'PTRF'
    assert result[1]['key'] == 'PDDE'
    assert result[2]['key'] == 'RECURSO_PROPRIO'


def test_get_objetivos_disponiveis(jwt_authenticated_client_sme, flag_paa, objetivo_paa_factory):

    objetivo_1 = objetivo_paa_factory()

    objetivo_paa_factory()

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(objetivo_1.paa.uuid)}/objetivos/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_atividades_estatutarias_disponiveis(jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_factory):

    atividade_1 = atividade_estatutaria_factory()
    atividade_estatutaria_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(atividade_1.paa.uuid)}/atividades-estatutarias-disponiveis/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_atividades_estatutarias_previstas(jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_paa_factory):

    atividade = atividade_estatutaria_paa_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(atividade.paa.uuid)}/atividades-estatutarias-previstas/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_recursos_proprios_previstos(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa_factory):

    recurso = recurso_proprio_paa_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(recurso.paa.uuid)}/recursos-proprios-previstos/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


@freeze_time('2025-06-15')
def test_get_paa_vigente_e_anteriores(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):
    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/paa-vigente-e-anteriores/?associacao_uuid={paa_2025.associacao.uuid}"
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result['vigente']['uuid'] == str(paa_2025.uuid)
    assert len(result['anteriores']) == 1
    assert result['anteriores'][0]['uuid'] == str(paa_2024.uuid)


@freeze_time('2026-01-01')
def test_get_paa_vigente_e_anteriores_sem_periodo(jwt_authenticated_client_sme, flag_paa, associacao, periodo_paa_factory):
    periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/paa-vigente-e-anteriores/?associacao_uuid={associacao.uuid}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
