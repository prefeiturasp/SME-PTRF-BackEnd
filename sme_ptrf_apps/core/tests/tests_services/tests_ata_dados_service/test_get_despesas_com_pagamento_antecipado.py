import datetime

import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import Recurso
from sme_ptrf_apps.core.services.ata_dados_service import get_despesas_com_pagamento_antecipado

pytestmark = pytest.mark.django_db


@pytest.fixture
def recurso_legado():
    return Recurso.objects.get(legado=True)


@pytest.fixture
def ata_para_pagamento_antecipado(associacao, ata_periodo_2020_1):
    return baker.make(
        'Ata',
        associacao=associacao,
        periodo=ata_periodo_2020_1,
        tipo_ata='APRESENTACAO',
        prestacao_conta=None,
        hora_reuniao=datetime.time(10, 0),
        data_reuniao=datetime.date(2020, 7, 10),
    )


@pytest.fixture
def despesa_pagamento_antecipado(associacao, tipo_documento, tipo_transacao, recurso_legado):
    """Despesa onde data_transacao < data_documento (pagamento antes do documento)."""
    return baker.make(
        'despesas.Despesa',
        associacao=associacao,
        numero_documento='DOC-001',
        data_documento=datetime.date(2020, 3, 20),
        data_transacao=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor Antecipado SA',
        valor_total=300.00,
        valor_recursos_proprios=0.00,
        recurso=recurso_legado,
    )


@pytest.fixture
def despesa_normal(associacao, tipo_documento, tipo_transacao, recurso_legado):
    """Despesa onde data_transacao >= data_documento (pagamento normal)."""
    return baker.make(
        'despesas.Despesa',
        associacao=associacao,
        numero_documento='DOC-002',
        data_documento=datetime.date(2020, 3, 10),
        data_transacao=datetime.date(2020, 3, 15),
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        cpf_cnpj_fornecedor='22.333.444/0001-55',
        nome_fornecedor='Fornecedor Normal SA',
        valor_total=150.00,
        valor_recursos_proprios=0.00,
        recurso=recurso_legado,
    )


def test_get_despesas_com_pagamento_antecipado_sem_despesas(ata_para_pagamento_antecipado):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert resultado == []


def test_get_despesas_com_pagamento_antecipado_despesa_normal_nao_incluida(
    ata_para_pagamento_antecipado, despesa_normal
):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert resultado == []


def test_get_despesas_com_pagamento_antecipado_inclui_pagamento_antecipado(
    ata_para_pagamento_antecipado, despesa_pagamento_antecipado
):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert len(resultado) == 1
    assert resultado[0]['nome_fornecedor'] == 'Fornecedor Antecipado SA'
    assert resultado[0]['numero_documento'] == 'DOC-001'


def test_get_despesas_com_pagamento_antecipado_estrutura_retorno(
    ata_para_pagamento_antecipado, despesa_pagamento_antecipado
):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert len(resultado) == 1
    item = resultado[0]
    assert 'nome_fornecedor' in item
    assert 'cpf_cnpj_fornecedor' in item
    assert 'tipo_documento' in item
    assert 'numero_documento' in item
    assert 'data_documento' in item
    assert 'tipo_transacao' in item
    assert 'data_transacao' in item
    assert 'valor_total' in item
    assert 'motivos_pagamento_antecipado' in item
    assert 'outros_motivos_pagamento_antecipado' in item


def test_get_despesas_com_pagamento_antecipado_valor_total(
    ata_para_pagamento_antecipado, despesa_pagamento_antecipado
):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    from decimal import Decimal
    assert resultado[0]['valor_total'] == Decimal('300.00')


def test_get_despesas_com_pagamento_antecipado_datas_formatadas(
    ata_para_pagamento_antecipado, despesa_pagamento_antecipado
):
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert resultado[0]['data_documento'] == '20/03/2020'
    assert resultado[0]['data_transacao'] == '10/03/2020'


def test_get_despesas_com_pagamento_antecipado_fora_do_periodo_nao_incluida(
    ata_para_pagamento_antecipado, associacao, tipo_documento, tipo_transacao
):
    """Despesa fora do período 2020.1 não deve ser incluída."""
    baker.make(
        'despesas.Despesa',
        associacao=associacao,
        numero_documento='DOC-FORA',
        data_documento=datetime.date(2019, 6, 20),
        data_transacao=datetime.date(2019, 6, 10),
        tipo_documento=tipo_documento,
        tipo_transacao=tipo_transacao,
        valor_total=50.00,
        valor_recursos_proprios=0.00,
    )
    resultado = get_despesas_com_pagamento_antecipado(ata=ata_para_pagamento_antecipado)
    assert resultado == []
