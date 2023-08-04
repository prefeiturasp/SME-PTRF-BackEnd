import pytest

from model_bakery import baker

from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao

@pytest.fixture
def payload_valido_solicitacao_encerramento(conta_associacao):
    payload = {
        'conta_associacao': str(conta_associacao.uuid),
        'data_de_encerramento_na_agencia': "2019-09-02",
    }
    return payload

@pytest.fixture
def payload_solicitacao_encerramento_data_invalida(conta_associacao):
    payload = {
        'conta_associacao': str(conta_associacao.uuid),
        'data_de_encerramento_na_agencia': "2019-08-31",
    }
    return payload

@pytest.fixture
def solicitacao_encerramento(conta_associacao):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao,
        data_de_encerramento_na_agencia='2019-09-02'
    )

@pytest.fixture
def solicitacao_encerramento_aprovada(conta_associacao):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao,
        data_de_encerramento_na_agencia='2019-09-02',
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA
    )

