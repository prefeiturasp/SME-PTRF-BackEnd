import pytest

from model_bakery import baker

from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao

@pytest.fixture
def motivo_rejeicao():
    return baker.make(
        'MotivoRejeicaoEncerramentoContaAssociacao',
        nome='Pix inválido'
    )

@pytest.fixture
def motivo_rejeicao_2():
    return baker.make(
        'MotivoRejeicaoEncerramentoContaAssociacao',
        nome='Conta inválida'
    )

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
def payload_rejeitar_solicitacao(motivo_rejeicao, motivo_rejeicao_2):
    payload = {
        'motivos_rejeicao': [f'{motivo_rejeicao.uuid}', f'{motivo_rejeicao_2.uuid}'],
        'outros_motivos_rejeicao': 'UE com pendências cadastrais.'
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

@pytest.fixture
def solicitacao_encerramento_reprovada(conta_associacao):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao,
        data_de_encerramento_na_agencia='2019-09-02',
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_REJEITADA
    )
