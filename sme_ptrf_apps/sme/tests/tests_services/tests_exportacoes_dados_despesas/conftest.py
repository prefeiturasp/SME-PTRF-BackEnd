import pytest

from datetime import date

from model_bakery import baker

from sme_ptrf_apps.despesas.models.despesa import Despesa

@pytest.fixture
def despesa_no_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        id=10,
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas,
        valor_total=300.00,
        valor_original=300,
        documento_transacao=312321
    )

@pytest.fixture
def outra_despesa_no_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        id=11,
        associacao=associacao,
        numero_documento='312323',
        data_documento=periodo.data_inicio_realizacao_despesas,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas,
        valor_total=100.00,
        valor_original=100,
        documento_transacao=231321
    )

@pytest.fixture
def queryset_ordered(despesa_no_periodo, outra_despesa_no_periodo):
    return Despesa.objects.all().order_by('criado_em')