import pytest
from model_bakery import baker

from ...models import Despesa
from ...status_cadastro_completo import STATUS_COMPLETO, STATUS_INCOMPLETO

pytestmark = pytest.mark.django_db


@pytest.fixture
def rateio_despesa_custeio_completo(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                                    tipo_custeio_servico, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,

    )


@pytest.fixture
def rateio_despesa_custeio_incompleto(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                                      tipo_custeio_servico, especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=0.00,  # Falta o valor

    )


@pytest.fixture
def rateio_despesa_capital_completo(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                    especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=10.00,  # Falta o valor
        quantidade_itens_capital=1,
        valor_item_capital=10.00,
        numero_processo_incorporacao_capital='teste123456'
    )


@pytest.fixture
def rateio_despesa_capital_incompleto(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                      especificacao_material_servico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=0.00,
        quantidade_itens_capital=0,
        valor_item_capital=0,
        numero_processo_incorporacao_capital=''
    )


@pytest.fixture
def despesa_incompleta(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=None,
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=None,
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


def test_despesa_completa(despesa):
    assert despesa.status == STATUS_COMPLETO


def test_despesa_incompleta(despesa_incompleta):
    assert despesa_incompleta.status == STATUS_INCOMPLETO


def test_rateio_despesa_custeio_completo(rateio_despesa_custeio_completo):
    assert rateio_despesa_custeio_completo.status == STATUS_COMPLETO


def test_rateio_despesa_custeio_incompleto(rateio_despesa_custeio_incompleto):
    assert rateio_despesa_custeio_incompleto.status == STATUS_INCOMPLETO
    despesa = Despesa.objects.get(uuid=rateio_despesa_custeio_incompleto.despesa.uuid)
    assert despesa.status == STATUS_INCOMPLETO


def test_rateio_despesa_capital_incompleto(rateio_despesa_capital_incompleto):
    assert rateio_despesa_capital_incompleto.status == STATUS_INCOMPLETO
    despesa = Despesa.objects.get(uuid=rateio_despesa_capital_incompleto.despesa.uuid)
    assert despesa.status == STATUS_INCOMPLETO


def test_rateio_despesa_capital_completo(rateio_despesa_capital_completo):
    assert rateio_despesa_capital_completo.status == STATUS_COMPLETO
    despesa = Despesa.objects.get(uuid=rateio_despesa_capital_completo.despesa.uuid)
    assert despesa.status == STATUS_COMPLETO


def test_despesa_de_transacao_que_tem_documento_com_documento(despesa_cheque_com_documento_transacao):
    # Despesa com tipo de transação que exige um documento de transação é completa quando tem o documento
    assert despesa_cheque_com_documento_transacao.status == STATUS_COMPLETO, "A despesa deveria estar completa"


def test_despesa_de_transacao_que_tem_documento_sem_documento(despesa_cheque_sem_documento_transacao):
    # Despesa com tipo de transação que exige um documento de transação é incompleta quando não tem o documento
    assert despesa_cheque_sem_documento_transacao.status == STATUS_INCOMPLETO, "A despesa deveria estar incompleta"


def test_despesa_de_transacao_que_nao_tem_documento_sem_documento(despesa_boleto_sem_documento_transacao):
    # Despesa com tipo de transação que não exige um documento de transação é completa mesmo sem o documento
    assert despesa_boleto_sem_documento_transacao.status == STATUS_COMPLETO, "A despesa deveria estar completa"
