import pytest

from datetime import date

from model_bakery import baker

@pytest.fixture
def motivo_pagamento_antecipado():
    return baker.make('MotivoPagamentoAntecipado', motivo='MotivoTeste')


@pytest.fixture
def despesa_com_motivo_pgto_antecipado(associacao, tipo_documento, tipo_transacao, motivo_pagamento_antecipado):
    despesa_com_motivo = baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2019, 9, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2025, 9, 10),
        valor_total=100.00,
    )
    despesa_com_motivo.motivos_pagamento_antecipado.set([motivo_pagamento_antecipado])
    # despesa_com_motivo.save()
    return despesa_com_motivo
