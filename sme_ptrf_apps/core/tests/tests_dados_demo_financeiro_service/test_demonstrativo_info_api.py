"""
Testes da action demonstrativo-info do DemonstrativoFinanceiroViewSet.

Garante que, ao consultar o período X, não seja exibida mensagem de prévia
de outro período (ex.: prévia de 2024 ao acessar 2025.3).
"""
import pytest
from datetime import date
from rest_framework import status

from sme_ptrf_apps.core.fixtures.factories.demonstrativo_financeiro_factory import (
    DemonstrativoFinanceiroFactory,
)
from sme_ptrf_apps.core.models import DemonstrativoFinanceiro

pytestmark = pytest.mark.django_db


def _get_msg(response):
    raw = response.content.decode("utf-8")
    return raw.strip('"') if raw.startswith('"') and raw.endswith('"') else raw


@pytest.fixture
def periodo_2024_1(periodo_factory, periodo):
    return periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 4, 30),
        periodo_anterior=periodo,
    )


@pytest.fixture
def periodo_2025_3(periodo_factory, periodo):
    return periodo_factory(
        referencia='2025.3',
        data_inicio_realizacao_despesas=date(2025, 9, 1),
        data_fim_realizacao_despesas=date(2025, 12, 31),
        periodo_anterior=periodo,
    )


def test_demonstrativo_info_periodo_sem_previa_nao_retorna_previa_de_outro_periodo(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    periodo_2024_1,
    periodo_2025_3,
):
    """
    Para o período 2025.3 não existe prévia nem prestação de contas.
    Existe apenas uma prévia antiga da mesma conta para 2024.1.
    A API deve retornar "Documento pendente de geração" e NÃO a mensagem
    da prévia de 2024
    """
    DemonstrativoFinanceiroFactory.create(
        conta_associacao=conta_associacao,
        periodo_previa=periodo_2024_1,
        prestacao_conta=None,
        versao=DemonstrativoFinanceiro.VERSAO_PREVIA,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )

    url = (
        f"/api/demonstrativo-financeiro/demonstrativo-info/"
        f"?conta-associacao={conta_associacao.uuid}&periodo={periodo_2025_3.uuid}"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    msg = _get_msg(response)
    assert msg == "Documento pendente de geração"
    assert "gerado dia" not in msg
    assert "22/04/2024" not in msg
    assert "prévio" not in msg


def test_demonstrativo_info_retorna_previa_quando_existe_para_o_periodo(
    jwt_authenticated_client_a,
    associacao,
    conta_associacao,
    periodo_2025_3,
):
    """Quando existe prévia para o período solicitado, retorna a mensagem com data."""
    DemonstrativoFinanceiroFactory.create(
        conta_associacao=conta_associacao,
        periodo_previa=periodo_2025_3,
        prestacao_conta=None,
        versao=DemonstrativoFinanceiro.VERSAO_PREVIA,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )

    url = (
        f"/api/demonstrativo-financeiro/demonstrativo-info/"
        f"?conta-associacao={conta_associacao.uuid}&periodo={periodo_2025_3.uuid}"
    )
    response = jwt_authenticated_client_a.get(url)

    assert response.status_code == status.HTTP_200_OK
    msg = _get_msg(response)
    assert "prévio" in msg
    assert "gerado dia" in msg
