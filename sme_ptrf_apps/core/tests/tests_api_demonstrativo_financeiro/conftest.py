import pytest
from datetime import date


@pytest.fixture
def periodo(periodo_factory):
    return periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 3, 31),
        data_prevista_repasse=date(2024, 1, 1),
        data_inicio_prestacao_contas=date(2024, 4, 1),
        data_fim_prestacao_contas=date(2024, 4, 15),
        periodo_anterior=None,
    )


@pytest.fixture
def periodo_aberto(periodo_factory):
    return periodo_factory(
        referencia='2024.2',
        data_inicio_realizacao_despesas=date(2024, 4, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2024, 4, 1),
        data_inicio_prestacao_contas=date(2024, 7, 1),
        data_fim_prestacao_contas=date(2024, 7, 15),
        periodo_anterior=None,
    )


@pytest.fixture
def conta_associacao(conta_associacao_factory):
    return conta_associacao_factory.create()


@pytest.fixture
def prestacao_conta(prestacao_conta_factory, conta_associacao, periodo):
    return prestacao_conta_factory.create(
        associacao=conta_associacao.associacao,
        periodo=periodo,
    )


@pytest.fixture
def demonstrativo_financeiro_final(demonstrativo_financeiro_factory, conta_associacao, prestacao_conta, periodo):
    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
    return demonstrativo_financeiro_factory.create(
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao_conta,
        periodo_previa=periodo,
        versao=DemonstrativoFinanceiro.VERSAO_FINAL,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )


@pytest.fixture
def demonstrativo_financeiro_previa(demonstrativo_financeiro_factory, conta_associacao, periodo):
    from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
    return demonstrativo_financeiro_factory.create(
        conta_associacao=conta_associacao,
        prestacao_conta=None,
        periodo_previa=periodo,
        versao=DemonstrativoFinanceiro.VERSAO_PREVIA,
        status=DemonstrativoFinanceiro.STATUS_CONCLUIDO,
    )


@pytest.fixture
def mock_arquivo_pdf():
    # FileField é persistido como varchar(100) no banco;
    # usar caminho absoluto de tmp_path pode estourar esse limite.
    return "dummy/demonstrativo_financeiro.pdf"


@pytest.fixture
def mock_arquivo_xlsx():
    # Mantém o caminho curto para evitar DataError ao salvar o FileField.
    return "dummy/demonstrativo_financeiro.xlsx"
