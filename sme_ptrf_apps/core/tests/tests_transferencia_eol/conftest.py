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
def transf_eol_acao_ptrf():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def transf_eol_acao_role():
    return baker.make('Acao', nome='Rolê Cultural')


@pytest.fixture
def transferencia_eol(tipo_conta, transf_eol_tipo_conta_cartao):
    return baker.make(
        'TransferenciaEol',
        eol_transferido='400232',
        eol_historico='900232',
        tipo_nova_unidade='CEMEI',
        cnpj_nova_associacao='44.445.671/0001-31',
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


@pytest.fixture
def transf_eol_associacao_eol_transferido(transf_eol_unidade_eol_transferido):
    return baker.make(
        'Associacao',
        nome='Escola Eol Transferido',
        cnpj='52.302.275/0001-83',
        unidade=transf_eol_unidade_eol_transferido,
    )


@pytest.fixture
def transf_eol_conta_associacao_cheque(
    transf_eol_associacao_eol_transferido,
    transf_eol_tipo_conta_cheque
):
    return baker.make(
        'ContaAssociacao',
        associacao=transf_eol_associacao_eol_transferido,
        tipo_conta=transf_eol_tipo_conta_cheque,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
    )


@pytest.fixture
def transf_eol_conta_associacao_cartao(
    transf_eol_associacao_eol_transferido,
    transf_eol_tipo_conta_cartao
):
    return baker.make(
        'ContaAssociacao',
        associacao=transf_eol_associacao_eol_transferido,
        tipo_conta=transf_eol_tipo_conta_cartao,
        banco_nome='ITAU',
        agencia='45678',
        numero_conta='999999-x',
    )


@pytest.fixture
def transf_eol_acao_associacao_ptrf(transf_eol_associacao_eol_transferido, transf_eol_acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=transf_eol_associacao_eol_transferido,
        acao=transf_eol_acao_ptrf
    )


@pytest.fixture
def transf_eol_acao_associacao_role(transf_eol_associacao_eol_transferido, transf_eol_acao_role):
    return baker.make(
        'AcaoAssociacao',
        associacao=transf_eol_associacao_eol_transferido,
        acao=transf_eol_acao_role
    )


@pytest.fixture
def transf_eol_fechamento_periodo(
    transf_eol_periodo_2022_2,
    transf_eol_associacao_eol_transferido,
    transf_eol_conta_associacao_cheque,
    transf_eol_acao_associacao_ptrf,
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=transf_eol_periodo_2022_2,
        associacao=transf_eol_associacao_eol_transferido,
        conta_associacao=transf_eol_conta_associacao_cheque,
        acao_associacao=transf_eol_acao_associacao_ptrf,
    )


@pytest.fixture
def transf_eol_despesa(
    transf_eol_associacao_eol_transferido,
    tipo_documento,
    tipo_transacao
):
    return baker.make(
        'Despesa',
        associacao=transf_eol_associacao_eol_transferido,
        numero_documento='123456',
        data_documento=datetime.date(2022, 7, 1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2022, 7, 1),
        valor_total=100.00,
    )


@pytest.fixture
def transf_eol_tipo_aplicacao_recurso_custeio():
    from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CUSTEIO
    return APLICACAO_CUSTEIO


@pytest.fixture
def transf_eol_especificacao_material_servico(transf_eol_tipo_aplicacao_recurso_custeio, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=transf_eol_tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
    )


@pytest.fixture
def transf_eol_rateio_despesa_conta_cheque(
    transf_eol_associacao_eol_transferido,
    transf_eol_despesa,
    transf_eol_conta_associacao_cheque,
    transf_eol_acao_associacao_ptrf,
    transf_eol_tipo_aplicacao_recurso_custeio,
    transf_eol_especificacao_material_servico,
    tipo_custeio,
):
    return baker.make(
        'RateioDespesa',
        despesa=transf_eol_despesa,
        associacao=transf_eol_associacao_eol_transferido,
        conta_associacao=transf_eol_conta_associacao_cheque,
        acao_associacao=transf_eol_acao_associacao_ptrf,
        aplicacao_recurso=transf_eol_tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=transf_eol_especificacao_material_servico,
        valor_rateio=200.00,
    )


@pytest.fixture
def transf_eol_rateio_despesa_conta_cartao(
    transf_eol_associacao_eol_transferido,
    transf_eol_despesa,
    transf_eol_conta_associacao_cartao,
    transf_eol_acao_associacao_ptrf,
    transf_eol_tipo_aplicacao_recurso_custeio,
    transf_eol_especificacao_material_servico,
    tipo_custeio,
):
    return baker.make(
        'RateioDespesa',
        despesa=transf_eol_despesa,
        associacao=transf_eol_associacao_eol_transferido,
        conta_associacao=transf_eol_conta_associacao_cartao,
        acao_associacao=transf_eol_acao_associacao_ptrf,
        aplicacao_recurso=transf_eol_tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=transf_eol_especificacao_material_servico,
        valor_rateio=100.00,
    )


@pytest.fixture
def transf_eol_unidade_eol_historico(dre):
    return baker.make(
        'Unidade',
        nome='Unidade EOL Transferido',
        tipo_unidade='CEMEI',
        codigo_eol='900232',
        dre=dre,
    )


@pytest.fixture
def transf_eol_associacao_nova(transf_eol_unidade_eol_historico, transferencia_eol):
    return baker.make(
        'Associacao',
        nome='Escola Eol Transferido',
        cnpj=transferencia_eol.cnpj_nova_associacao,
        unidade=transf_eol_unidade_eol_historico,
    )

