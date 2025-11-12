import pytest
import json
from datetime import date
from rest_framework import status
from sme_ptrf_apps.paa.models import AtividadeEstatutaria, AtividadeEstatutariaPaa

pytestmark = pytest.mark.django_db


def test_patch_objetivos_paa(jwt_authenticated_client_sme, flag_paa, objetivo_paa_factory):

    objetivo_1 = objetivo_paa_factory()

    payload = {
        "objetivos": [
            {"nome": "Objetivo novo"},
            {"objetivo": f"{objetivo_1.uuid}", "nome": "Novo nome objetivo existente"},
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{str(objetivo_1.paa.uuid)}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result['texto_introducao'] is None
    assert result['texto_conclusao'] is None
    assert len(result['objetivos']) == 2
    assert payload["objetivos"][1]["nome"] == "Novo nome objetivo existente"


def test_patch_atividades_estatutarias_nova_atividade(jwt_authenticated_client_sme, paa_factory):
    paa = paa_factory()

    payload = {
        "atividades_estatutarias": [
            {
                "nome": "Reunião",
                "tipo": "ORDINARIA",
                "data": "2025-01-10"
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = response.json()

    assert response.status_code == 200
    assert len(result["atividades_estatutarias_paa"]) > 0
    assert AtividadeEstatutaria.objects.filter(nome="Reunião").exists()
    assert AtividadeEstatutariaPaa.objects.filter(paa=paa).exists()


def test_patch_vincular_atividade_global(jwt_authenticated_client_sme, paa_factory, atividade_estatutaria_factory):
    paa = paa_factory()
    atividade_global = atividade_estatutaria_factory(paa=None)

    payload = {
        "atividades_estatutarias": [
            {
                "atividade_estatutaria": str(atividade_global.uuid),
                "data": "2025-02-05"
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert AtividadeEstatutariaPaa.objects.filter(paa=paa, atividade_estatutaria=atividade_global).exists()


def test_patch_editar_atividade_do_paa(jwt_authenticated_client_sme, paa_factory, atividade_estatutaria_factory):
    paa = paa_factory()
    atividade = atividade_estatutaria_factory(paa=paa, nome="Reunião antiga")

    payload = {
        "atividades_estatutarias": [
            {
                "atividade_estatutaria": str(atividade.uuid),
                "nome": "Reunião atualizada",
                "tipo": "ORDINARIA",
                "data": "2025-05-10"
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    atividade.refresh_from_db()
    assert atividade.nome == "Reunião atualizada"
    assert AtividadeEstatutariaPaa.objects.filter(
        paa=paa, atividade_estatutaria=atividade, data=date(2025, 5, 10)).exists()


def test_patch_excluir_atividade_do_paa(jwt_authenticated_client_sme, paa_factory, atividade_estatutaria_factory, atividade_estatutaria_paa_factory):
    paa = paa_factory()
    atividade = atividade_estatutaria_factory(paa=paa)
    atividade_estatutaria_paa_factory(atividade_estatutaria=atividade, paa=paa)

    payload = {
        "atividades_estatutarias": [
            {
                "atividade_estatutaria": str(atividade.uuid),
                "_destroy": True
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert not AtividadeEstatutaria.objects.filter(id=atividade.id).exists()
    assert not AtividadeEstatutariaPaa.objects.filter(paa=paa).exists()


def test_patch_nao_pode_excluir_atividade_global(jwt_authenticated_client_sme, paa_factory, atividade_estatutaria_factory):
    paa = paa_factory()
    atividade_global = atividade_estatutaria_factory(paa=None)

    payload = {
        "atividades_estatutarias": [
            {
                "atividade_estatutaria": str(atividade_global.uuid),
                "_destroy": True
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert AtividadeEstatutaria.objects.filter(id=atividade_global.id).exists()


def test_patch_impedir_duplicidade(jwt_authenticated_client_sme, paa_factory, atividade_estatutaria_factory):
    paa = paa_factory()

    atividade_estatutaria_factory(
        nome="Reunião",
        tipo="ORDINARIA",
        mes=1,
        paa=paa
    )

    payload = {
        "atividades_estatutarias": [
            {
                "nome": "Reunião",
                "tipo": "ORDINARIA",
                "data": "2025-01-10"
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert "já existe uma atividade" in response.json()["mensagem"].lower()


def test_patch_nova_sem_campos_obrigatorios(jwt_authenticated_client_sme, paa_factory):
    paa = paa_factory()

    payload = {
        "atividades_estatutarias": [
            {
                "nome": "Reunião"
            }
        ]
    }

    response = jwt_authenticated_client_sme.patch(
        f"/api/paa/{paa.uuid}/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert "precisa de nome, tipo e data" in response.json()["mensagem"].lower()
