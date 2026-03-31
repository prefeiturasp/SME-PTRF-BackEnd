import json
from datetime import date

import pytest
from rest_framework import status

from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_lancamento_factory import (
    TipoAcertoLancamentoFactory,
)
from sme_ptrf_apps.core.models import TipoAcertoLancamento
from sme_ptrf_apps.despesas.models import Despesa

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_acerto_lancamento_exclusao():
    return TipoAcertoLancamentoFactory(
        nome='Exclusão (teste período anterior)',
        categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
    )


@pytest.fixture
def tipo_acerto_lancamento_conciliacao():
    return TipoAcertoLancamentoFactory(
        nome='Conciliação (teste período anterior)',
        categoria=TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
    )


def _payload_solicitacao_gasto_unico(
    analise_uuid,
    despesa_uuid,
    tipo_acerto_uuid,
    detalhamento='Teste acerto despesa período anterior',
):
    return {
        'analise_prestacao': str(analise_uuid),
        'lancamentos': [
            {
                'tipo_lancamento': 'GASTO',
                'lancamento_uuid': str(despesa_uuid),
            },
        ],
        'solicitacoes_acerto': [
            {
                'uuid': None,
                'copiado': False,
                'tipo_acerto': str(tipo_acerto_uuid),
                'detalhamento': detalhamento,
                'devolucao_tesouro': None,
            },
        ],
    }


def test_post_solicitacoes_acerto_rejeita_exclusao_para_gasto_com_data_anterior_ao_periodo_da_pc(
    jwt_authenticated_client_a,
    despesa_2020_1,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_acerto_lancamento_exclusao,
):
    """
    __valida_tipos_acerto_para_despesa_periodo_anterior: gasto com data_transacao antes de
    data_inicio_realizacao_despesas do período da PC não pode receber solicitação nova de
    tipo que não seja conciliação/desconciliação.
    """
    periodo = prestacao_conta_2020_1_em_analise.periodo
    assert periodo.data_inicio_realizacao_despesas == date(2020, 1, 1)

    Despesa.objects.filter(pk=despesa_2020_1.pk).update(
        data_transacao=date(2019, 12, 15),
        data_documento=date(2019, 12, 15),
    )

    payload = _payload_solicitacao_gasto_unico(
        analise_prestacao_conta_2020_1_em_analise.uuid,
        despesa_2020_1.uuid,
        tipo_acerto_lancamento_exclusao.uuid,
    )

    url = (
        f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/'
        f'solicitacoes-de-acerto/'
    )
    response = jwt_authenticated_client_a.post(
        url, data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    body = json.loads(response.content)
    assert body['erro'] == 'solicita_acertos_de_lancamentos'
    assert 'Para despesas de períodos anteriores' in body['mensagem']
    assert 'conciliação' in body['mensagem'].lower() or 'desconciliação' in body['mensagem'].lower()


def test_post_solicitacoes_acerto_permite_conciliacao_para_gasto_com_data_anterior_ao_periodo_da_pc(
    jwt_authenticated_client_a,
    despesa_2020_1,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_acerto_lancamento_conciliacao,
):
    Despesa.objects.filter(pk=despesa_2020_1.pk).update(
        data_transacao=date(2019, 12, 15),
        data_documento=date(2019, 12, 15),
    )

    payload = _payload_solicitacao_gasto_unico(
        analise_prestacao_conta_2020_1_em_analise.uuid,
        despesa_2020_1.uuid,
        tipo_acerto_lancamento_conciliacao.uuid,
    )

    url = (
        f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/'
        f'solicitacoes-de-acerto/'
    )
    response = jwt_authenticated_client_a.post(
        url, data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content) == {
        'message': 'Solicitações de acerto gravadas para os lançamentos.'
    }


def test_post_solicitacoes_acerto_nao_aplica_validacao_quando_data_transacao_dentro_do_periodo_da_pc(
    jwt_authenticated_client_a,
    despesa_2020_1,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_acerto_lancamento_exclusao,
):
    """Com data no próprio período da PC, a validação de 'período anterior' não deve bloquear exclusão."""
    assert despesa_2020_1.data_transacao >= prestacao_conta_2020_1_em_analise.periodo.data_inicio_realizacao_despesas

    payload = _payload_solicitacao_gasto_unico(
        analise_prestacao_conta_2020_1_em_analise.uuid,
        despesa_2020_1.uuid,
        tipo_acerto_lancamento_exclusao.uuid,
    )

    url = (
        f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/'
        f'solicitacoes-de-acerto/'
    )
    response = jwt_authenticated_client_a.post(
        url, data=json.dumps(payload), content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
