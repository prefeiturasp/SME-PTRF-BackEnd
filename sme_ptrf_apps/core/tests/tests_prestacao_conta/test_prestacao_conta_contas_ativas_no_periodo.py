import pytest
from model_bakery import baker


pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta_teste_conta_ativa_no_periodo_19_02(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def prestacao_conta_teste_conta_ativa_no_periodo_20_1(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        status="EM_ANALISE"
    )


def test_contas_ativas_no_periodo_com_conta_encerrada_no_periodo_da_pc(
    conta_associacao_cheque,
    conta_associacao_cartao,
    conta_associacao_inativa,
    solicitacao_encerramento_conta_associacao,
    prestacao_conta_teste_conta_ativa_no_periodo_19_02
):

    # Todas as contas devem ser retornadas, pois a 'conta_associacao_inativa' foi inativada no periodo dessa PC
    contas_ativas_nesse_periodo = prestacao_conta_teste_conta_ativa_no_periodo_19_02.contas_ativas_no_periodo()

    assert len(contas_ativas_nesse_periodo) == 3
    assert conta_associacao_cheque in contas_ativas_nesse_periodo
    assert conta_associacao_cartao in contas_ativas_nesse_periodo
    assert conta_associacao_inativa in contas_ativas_nesse_periodo


def test_contas_ativas_no_periodo_com_conta_encerrada_no_periodo_anterior_da_pc(
    conta_associacao_cheque,
    conta_associacao_cartao,
    conta_associacao_inativa,
    solicitacao_encerramento_conta_associacao,
    prestacao_conta_teste_conta_ativa_no_periodo_20_1
):

    # A conta 'conta_associacao_inativa' não deve ser retornada, pois foi encerrada no periodo anterior a PC
    contas_ativas_nesse_periodo = prestacao_conta_teste_conta_ativa_no_periodo_20_1.contas_ativas_no_periodo()

    assert len(contas_ativas_nesse_periodo) == 2
    assert conta_associacao_cheque in contas_ativas_nesse_periodo
    assert conta_associacao_cartao in contas_ativas_nesse_periodo
    assert conta_associacao_inativa not in contas_ativas_nesse_periodo


def test_contas_ativas_no_periodo_com_conta_encerrada_no_periodo_posterior_da_pc(
    conta_associacao_cheque,
    conta_associacao_cartao,
    conta_associacao_inativa_x,
    solicitacao_encerramento_conta_associacao_no_periodo_2020_1,
    prestacao_conta_teste_conta_ativa_no_periodo_19_02
):

    # Todas as contas devem ser retornadas, a 'conta_associacao_inativa' foi inativada no periodo posterior dessa PC
    contas_ativas_nesse_periodo = prestacao_conta_teste_conta_ativa_no_periodo_19_02.contas_ativas_no_periodo()

    assert len(contas_ativas_nesse_periodo) == 3
    assert conta_associacao_cheque in contas_ativas_nesse_periodo
    assert conta_associacao_cartao in contas_ativas_nesse_periodo
    assert conta_associacao_inativa_x in contas_ativas_nesse_periodo

