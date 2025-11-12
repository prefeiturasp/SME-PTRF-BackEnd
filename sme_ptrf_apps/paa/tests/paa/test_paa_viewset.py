import pytest
import json
from datetime import datetime, date
from freezegun import freeze_time
from rest_framework import status
from sme_ptrf_apps.paa.models import Paa, PrioridadePaa
from django.urls import reverse
from sme_ptrf_apps.paa.models import AtividadeEstatutaria, AtividadeEstatutariaPaa

pytestmark = pytest.mark.django_db


@freeze_time('2025-01-01')
def test_desativar_atualizacao_saldo(
        jwt_authenticated_client_sme, periodo_paa_2025_1, flag_paa, paa_factory, acao_associacao_factory):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
    )

    acao_associacao_factory.create(associacao=paa.associacao)
    acao_associacao_factory.create(associacao=paa.associacao)

    response = jwt_authenticated_client_sme.post(f"/api/paa/{paa.uuid}/desativar-atualizacao-saldo/")

    result = response.json()
    paa = Paa.objects.get(id=paa.id)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
    assert paa.saldo_congelado_em == datetime(2025, 1, 1, 0, 0)


def test_ativar_atualizacao_saldo(
        jwt_authenticated_client_sme, periodo_paa_2025_1, flag_paa, paa_factory, acao_associacao_factory):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_2025_1,
    )

    acao_associacao_factory.create(associacao=paa.associacao)
    acao_associacao_factory.create(associacao=paa.associacao)

    response = jwt_authenticated_client_sme.post(f"/api/paa/{paa.uuid}/ativar-atualizacao-saldo/")

    result = response.json()
    paa = Paa.objects.get(id=paa.id)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
    assert paa.saldo_congelado_em is None


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


def test_action_importar_prioridades_paa_atual_nao_encontrado(
        jwt_authenticated_client_sme, flag_paa):

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": "11111111-1111-1111-1111-111111111111",
            "uuid_paa_anterior": "22222222-2222-2222-2222-222222222222",
        },
    )

    response = jwt_authenticated_client_sme.post(url)

    result = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == {"mensagem": "PAA atual não encontrado."}


def test_action_importar_prioridades_paa_anterior_nao_encontrado(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory):

    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2025 = paa_factory.create(periodo_paa=periodo_2025)

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": "22222222-2222-2222-2222-222222222222",
        },
    )

    response = jwt_authenticated_client_sme.post(url)

    result = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result == {"mensagem": "PAA anterior não encontrado."}


def test_action_importar_prioridades_com_sucesso(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory, prioridade_paa_factory):

    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    # considerar mesma associacao
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    for i in range(0, 10):
        # simular pelo menos 1 prioridade com o campo prioridade == Não
        # Em vez de validar 10 prioridades importadas, deverá importar apenas 9
        prioridade_paa_factory.create(paa=paa_2024, prioridade=i != 0)

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": str(paa_2024.uuid),
        },
    )

    response = jwt_authenticated_client_sme.post(url)

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result == {'mensagem': 'Prioridades importadas com sucesso.'}

    prioridades_2024 = PrioridadePaa.objects.filter(paa_id=paa_2024.id)
    assert prioridades_2024.count() == 10

    prioridades_2025 = PrioridadePaa.objects.filter(paa_id=paa_2025.id)
    assert prioridades_2025.count() == 9  # 1 não importado por estar como prioridade == Não (índice 0)

    assert prioridades_2024.count() != prioridades_2025.count()


def test_action_importar_prioridades_sem_prioridades_paa_anterior(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory, prioridade_paa_factory):

    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": str(paa_2024.uuid),
        },
    )

    response = jwt_authenticated_client_sme.post(url)
    result = response.json()
    response_esperado = {'mensagem': 'Nenhuma prioridade encontrada para importação.'}

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == response_esperado

    prioridades_2024 = PrioridadePaa.objects.filter(paa_id=paa_2024.id)
    assert prioridades_2024.count() == 0

    prioridades_2025 = PrioridadePaa.objects.filter(paa_id=paa_2025.id)
    assert prioridades_2025.count() == 0


def test_action_importar_prioridades_quando_ja_houver_prioridades_importadas_e_sem_confirmacao(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory, prioridade_paa_factory):

    periodo_2023 = periodo_paa_factory.create(
        referencia="Periodo 2023", data_inicial=date(2023, 1, 1), data_final=date(2023, 12, 31))
    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2023 = paa_factory.create(periodo_paa=periodo_2023)
    paa_2024 = paa_factory.create(periodo_paa=periodo_2024, associacao=paa_2023.associacao)
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    # prioridade 2024 para simular importação em 2025
    prioridade_paa_factory.create(paa=paa_2024, prioridade=True)
    # prioridades importadas de 2023 já existentes em 2025
    prioridade_paa_factory.create(paa=paa_2025, prioridade=True, paa_importado=paa_2023)

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": str(paa_2024.uuid),
        },
    )

    response = jwt_authenticated_client_sme.post(url)
    result = response.json()
    response_esperado = {'confirmar': (
        "Foi realizada a importação de um PAA anteriormente e todas as prioridades deste PAA anterior "
        "serão excluídas e será realizada a importação do PAA indicado."
    )}

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == response_esperado


def test_action_importar_prioridades_quando_ja_houver_prioridades_importadas_e_com_confirmacao(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory, prioridade_paa_factory):

    periodo_2023 = periodo_paa_factory.create(
        referencia="Periodo 2023", data_inicial=date(2023, 1, 1), data_final=date(2023, 12, 31))
    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2023 = paa_factory.create(periodo_paa=periodo_2023)
    paa_2024 = paa_factory.create(periodo_paa=periodo_2024, associacao=paa_2023.associacao)
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    # prioridade 2024 para simular importação em 2025
    prioridade_paa_factory.create(paa=paa_2024, prioridade=True)

    prioridade_paa_factory.create(paa=paa_2025, prioridade=True, paa_importado=paa_2023)

    # valida a existencia de Prioridades importadas de 2023 em 2025
    prioridades_importadas_2023_em_2025 = PrioridadePaa.objects.filter(paa_id=paa_2025.id, paa_importado_id=paa_2023.id)
    assert prioridades_importadas_2023_em_2025.count() == 1

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": str(paa_2024.uuid),
        },
    )
    url += "?confirmar=1"

    response = jwt_authenticated_client_sme.post(url)

    result = response.json()

    response_esperado = {'mensagem': (
        "Prioridades importadas com sucesso."
    )}

    assert response.status_code == status.HTTP_200_OK
    assert result == response_esperado

    # valida a exclusão de Prioridades importadas de 2023 em 2025
    prioridades_importadas_2023_em_2025 = PrioridadePaa.objects.filter(paa_id=paa_2025.id, paa_importado_id=paa_2023.id)
    assert prioridades_importadas_2023_em_2025.count() == 0  # Removidas após confirmação

    # valida a importação de Prioridades importadas de 2024 em 2025 após a confirmação
    prioridades_importadas_2024_em_2025 = PrioridadePaa.objects.filter(paa_id=paa_2025.id, paa_importado_id=paa_2024.id)
    assert prioridades_importadas_2024_em_2025.count() == 1  # Importadas após confirmação


def test_action_importar_prioridades_quando_ja_houver_prioridades_importadas_do_mesmo_paa(
        jwt_authenticated_client_sme, flag_paa, periodo_paa_factory, paa_factory, prioridade_paa_factory):

    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    # considerar mesma associacao
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    # prioridade 2024 para simular importação em 2025
    prioridade_paa_factory.create(paa=paa_2024, prioridade=True)
    # prioridades importadas de 2024 em 2025
    prioridade_paa_factory.create(paa=paa_2025, prioridade=True, paa_importado=paa_2024)

    url = reverse(
        "api:paa-importar-prioridades",
        kwargs={
            "uuid": str(paa_2025.uuid),
            "uuid_paa_anterior": str(paa_2024.uuid),
        },
    )

    response = jwt_authenticated_client_sme.post(url)

    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {'mensagem': 'Não é permitido importar novamente o mesmo PAA.'}


def test_get_objetivos_paa(jwt_authenticated_client_sme, flag_paa, objetivo_paa_factory):

    objetivo_1 = objetivo_paa_factory()

    objetivo_paa_factory()

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(objetivo_1.paa.uuid)}/objetivos-disponiveis/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


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


def test_get_atividades_estatutarias_disponiveis_paa(jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_factory):

    atividade_1 = atividade_estatutaria_factory()
    atividade_estatutaria_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(atividade_1.paa.uuid)}/atividades-estatutarias-disponiveis/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


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
