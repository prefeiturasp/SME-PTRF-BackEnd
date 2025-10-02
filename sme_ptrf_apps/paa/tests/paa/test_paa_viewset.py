import pytest
from datetime import datetime, date
from freezegun import freeze_time
from rest_framework import status
from sme_ptrf_apps.paa.models import Paa, PrioridadePaa
from django.urls import reverse

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
