import json
import datetime
import pytest

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_2020_1_teste_analises(periodo_2020_1, associacao):
    # Aqui PC
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 10, 1),
        status="EM_ANALISE"
    )


@pytest.fixture
def devolucao_prestacao_conta_2020_1_teste_analises(prestacao_conta_2020_1_teste_analises):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        data=datetime.date(2020, 10, 5),
        data_limite_ue=datetime.date(2020, 8, 1),
    )

@pytest.fixture
def analise_prestacao_conta_2020_1_devolvida(
    prestacao_conta_2020_1_teste_analises,
    devolucao_prestacao_conta_2020_1_teste_analises
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=devolucao_prestacao_conta_2020_1_teste_analises,
        status='DEVOLVIDA'
    )


@pytest.fixture
def analise_prestacao_conta_2020_1_aprovada(
    prestacao_conta_2020_1_teste_analises,
):
    return baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_teste_analises,
        devolucao_prestacao_conta=None,
        status='APROVADA'
    )


def test_api_analise_prestacao_contas_list_devolucoes(
    jwt_authenticated_client_a,
    analise_prestacao_conta_2020_1_devolvida,
    analise_prestacao_conta_2020_1_aprovada
):
    analise_prestacao = analise_prestacao_conta_2020_1_devolvida
    prestacao_conta = analise_prestacao.prestacao_conta

    result_esperado = [
        {
            'criado_em': analise_prestacao.criado_em.isoformat("T"),
            'devolucao_prestacao_conta': {'cobrancas_da_devolucao': [],
                                          'data': '2020-10-05',
                                          'data_limite_ue': '2020-08-01',
                                          'data_retorno_ue': None,
                                          'prestacao_conta': f'{analise_prestacao.prestacao_conta.uuid}',
                                          'uuid': f'{analise_prestacao.devolucao_prestacao_conta.uuid}'},
            'id': analise_prestacao.id,
            'prestacao_conta': f'{prestacao_conta.uuid}',
            'status': 'DEVOLVIDA',
            'uuid': f'{analise_prestacao.uuid}',
            'versao': analise_prestacao.versao
        },
    ]

    url = f'/api/prestacoes-contas/{prestacao_conta.uuid}/devolucoes/'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
