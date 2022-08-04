import pytest
from model_bakery import baker


@pytest.fixture
def analise_lancamento_pendente_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="PENDENTE"
    )


@pytest.fixture
def analise_lancamento_realizado_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_lancamento_realizado_02(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="REALIZADO"
    )


@pytest.fixture
def analise_lancamento_justificado_01(analise_prestacao_conta_2020_1):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=None,
        resultado='CORRETO',
        justificativa="teste",
        status_realizacao="JUSTIFICADO"
    )
