import pytest
from datetime import date
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_contas_com_acertos_em_despesas_periodos_anteriores(
    jwt_authenticated_client_a,
    periodo_factory,
    associacao_factory,
    conta_associacao_factory,
    analise_prestacao_conta_factory,
    prestacao_conta_factory,
    despesa_factory,
    rateio_despesa_factory,
    analise_lancamento_prestacao_conta_factory,
    acao_factory,
    acao_associacao_factory
):
    acao = acao_factory()
    associacao = associacao_factory()
    periodo_2024_1 = periodo_factory(
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 6, 1),
        referencia='2024.1',
    )
    acao_associacao = acao_associacao_factory(associacao=associacao, acao=acao)
    conta_associacao = conta_associacao_factory(associacao=associacao)
    pc = prestacao_conta_factory(associacao=associacao, periodo=periodo_2024_1)
    analise = analise_prestacao_conta_factory(prestacao_conta=pc)
    despesa = despesa_factory(data_transacao=date(2023, 6, 2), valor_total=100, associacao=associacao)
    rateio_despesa_factory(
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        despesa=despesa,
        associacao=associacao,
        valor_rateio=100,
        conferido=False,
        update_conferido=False,
        aplicacao_recurso='CUSTEIO'
    )
    analise_lancamento_prestacao_conta_factory(analise_prestacao_conta=analise, despesa=despesa)

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/contas-com-acertos-em-despesas-periodos-anteriores/?associacao_uuid={associacao.uuid}&analise_prestacao_uuid={analise.uuid}',
        content_type='application/json'
    )

    assert len(response.json()) == 1
    assert response.status_code == status.HTTP_200_OK
