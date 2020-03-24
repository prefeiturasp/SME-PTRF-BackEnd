import pytest
import datetime

from model_bakery import baker


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe')


@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')


@pytest.fixture
def tipo_aplicacao_recurso():
    return baker.make('TipoAplicacaoRecurso', nome='Custeio')


@pytest.fixture
def especificacao_material_servico(tipo_aplicacao_recurso, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        tipo_aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
    )


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
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_capital(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                           especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )
