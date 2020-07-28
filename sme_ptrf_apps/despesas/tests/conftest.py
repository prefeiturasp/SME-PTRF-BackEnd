import datetime

import pytest
from model_bakery import baker

from ..tipos_aplicacao_recurso import APLICACAO_CUSTEIO, APLICACAO_CAPITAL


@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe', apenas_digitos=False, numero_documento_digitado=False)

@pytest.fixture
def tipo_documento_numero_documento_digitado():
    return baker.make('TipoDocumento', nome='NFe', apenas_digitos=False, numero_documento_digitado=True)

@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')

@pytest.fixture
def tipo_transacao_cheque_com_documento():
    return baker.make('TipoTransacao', nome='Cheque', tem_documento=True)

@pytest.fixture
def tipo_transacao_boleto_sem_documento():
    return baker.make('TipoTransacao', nome='Boleto', tem_documento=False)

@pytest.fixture
def tipo_aplicacao_recurso():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_custeio():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_capital():
    return APLICACAO_CAPITAL


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_custeio_material():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_custeio_servico():
    return baker.make('TipoCusteio', nome='Servico')


@pytest.fixture
def especificacao_material_servico(tipo_aplicacao_recurso, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
    )


@pytest.fixture
def especificacao_custeio_material(tipo_aplicacao_recurso_custeio, tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
    )


@pytest.fixture
def especificacao_custeio_servico(tipo_aplicacao_recurso_custeio, tipo_custeio_servico):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Instalação elétrica',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
    )


@pytest.fixture
def especificacao_material_eletrico(especificacao_custeio_material):
    return especificacao_custeio_material


@pytest.fixture
def especificacao_instalacao_eletrica(especificacao_custeio_servico):
    return especificacao_custeio_servico


@pytest.fixture
def especificacao_capital(tipo_aplicacao_recurso_capital):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Ar condicionado',
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


@pytest.fixture
def especificacao_ar_condicionado(especificacao_capital):
    return especificacao_capital


@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def despesa_cheque_com_documento_transacao(associacao, tipo_documento, tipo_transacao_cheque_com_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_cheque_com_documento,
        documento_transacao='123456789',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )

@pytest.fixture
def despesa_cheque_sem_documento_transacao(associacao, tipo_documento, tipo_transacao_cheque_com_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_cheque_com_documento,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )

@pytest.fixture
def despesa_boleto_sem_documento_transacao(associacao, tipo_documento, tipo_transacao_boleto_sem_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_boleto_sem_documento,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )

@pytest.fixture
def rateio_despesa_capital(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                           especificacao_material_servico, acao_associacao, prestacao_conta_iniciada):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456',
        conferido=True,
        prestacao_conta=prestacao_conta_iniciada,
    )


@pytest.fixture
def rateio_despesa_instalacao_eletrica_ptrf(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_servico,
                                            especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_material_eletrico_role_cultural(associacao, despesa, conta_associacao, acao,
                                                   tipo_aplicacao_recurso_custeio,
                                                   tipo_custeio_material,
                                                   especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00,
        conferido=False,

    )

@pytest.fixture
def rateio_despesa_ar_condicionado_ptrf(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                        especificacao_ar_condicionado, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )

@pytest.fixture
def rateio_despesa_conferido(rateio_despesa_instalacao_eletrica_ptrf):
    return rateio_despesa_instalacao_eletrica_ptrf

@pytest.fixture
def rateio_despesa_nao_conferido(rateio_despesa_material_eletrico_role_cultural):
    return rateio_despesa_material_eletrico_role_cultural

@pytest.fixture
def rateio_despesa_nao_conferido2(rateio_despesa_ar_condicionado_ptrf):
    return rateio_despesa_ar_condicionado_ptrf

@pytest.fixture
def fornecedor_jose():
    return baker.make('Fornecedor', nome='José', cpf_cnpj='079.962.460-84')


@pytest.fixture
def fornecedor_industrias_teste():
    return baker.make('Fornecedor', nome='Indústrias Teste', cpf_cnpj='80.554.237/0001-53')
