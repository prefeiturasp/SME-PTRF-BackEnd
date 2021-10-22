import json
import datetime
import pytest

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_2020_1_teste_get_ultima_analise(periodo_2020_1, associacao):
    # Aqui PC
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )


@pytest.fixture
def devolucao_prestacao_conta_2020_1_teste_get_ultima_analise(prestacao_conta_2020_1_teste_get_ultima_analise):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_get_ultima_analise,
        data=datetime.date(2020, 10, 5),
        data_limite_ue=datetime.date(2020, 8, 1),
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_devolvida(
    prestacao_conta_2020_1_teste_get_ultima_analise,
    devolucao_prestacao_conta_2020_1_teste_get_ultima_analise
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_get_ultima_analise,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_get_ultima_analise,
        status='DEVOLVIDA'
    )


def test_get_ultima_analise_pc(jwt_authenticated_client_a, analise_prestacao_conta_2020_1_devolvida):
    analise_prestacao = analise_prestacao_conta_2020_1_devolvida
    prestacao_conta = analise_prestacao.prestacao_conta

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/ultima-analise-pc/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    result_esperado = {
            'uuid': f'{result["uuid"]}',
            'id': result["id"],
            'prestacao_conta': f'{prestacao_conta.uuid}',
            'devolucao_prestacao_conta': {
                'uuid': f'{analise_prestacao.devolucao_prestacao_conta.uuid}',
                'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
                'data': '2020-10-05', 'data_limite_ue': '2020-08-01',
                'cobrancas_da_devolucao': []
            },
            'status': 'DEVOLVIDA',
            'criado_em': analise_prestacao.criado_em.isoformat("T"),
        }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
