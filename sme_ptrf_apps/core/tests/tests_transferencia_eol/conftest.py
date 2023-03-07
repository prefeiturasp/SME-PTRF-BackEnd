import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def transf_eol_periodo_2022_2():
    return baker.make(
        'Periodo',
        referencia='2022.2',
        data_inicio_realizacao_despesas=datetime.date(2022, 7, 1),
        data_fim_realizacao_despesas=datetime.date(2022, 12, 31),
        periodo_anterior=None
    )

@pytest.fixture
def transf_eol_tipo_conta_cheque():
    return baker.make(
        'TipoConta',
        nome='Cheque',
    )


@pytest.fixture
def transf_eol_tipo_conta_cartao():
    return baker.make(
        'TipoConta',
        nome='Cartão',
    )


@pytest.fixture
def transferencia_eol(tipo_conta, transf_eol_tipo_conta_cartao):
    return baker.make(
        'TransferenciaEol',
        eol_transferido='400232',
        eol_historico='900232',
        tipo_nova_unidade='CEMEI',
        data_inicio_atividades=datetime.date(2022, 7, 1),
        tipo_conta_transferido=transf_eol_tipo_conta_cartao,
        status_processamento='PENDENTE',
        log_execucao='Teste',
    )


@pytest.fixture
def transf_eol_unidade_eol_transferido(dre):
    return baker.make(
        'Unidade',
        nome='Unidade EOL Transferido',
        tipo_unidade='CEI',
        codigo_eol='400232',
        dre=dre,
    )


@pytest.fixture
def transf_eol_unidade_eol_historico_ja_existente(dre):
    return baker.make(
        'Unidade',
        nome='Unidade Histórico',
        tipo_unidade='CEMEI',
        codigo_eol='900232',
        dre=dre,
    )
