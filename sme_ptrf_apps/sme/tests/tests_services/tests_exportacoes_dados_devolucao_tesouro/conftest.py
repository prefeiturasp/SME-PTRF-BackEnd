import pytest
from datetime import date
from model_bakery import baker

from sme_ptrf_apps.core.models.solicitacao_devolucao_ao_tesouro import SolicitacaoDevolucaoAoTesouro

pytestmark = pytest.mark.django_db

@pytest.fixture
def rateio_despesa_01(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        valor_original=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00
    )

@pytest.fixture
def rateio_despesa_02(associacao, despesa_no_periodo, conta_associacao, acao,tipo_aplicacao_recurso_custeio, tipo_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio,
        valor_rateio=100.00,
        valor_original=100.00,
    )

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
def analise_lancamento_receita_prestacao_conta_2020_1(analise_prestacao_conta_2020_1, receita_no_periodo_2020_1, despesa_no_periodo):
    return baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_prestacao_conta_2020_1,
        tipo_lancamento='CREDITO',
        receita=receita_no_periodo_2020_1,
        resultado='CORRETO',
        despesa=despesa_no_periodo
    )

@pytest.fixture
def solicitacao_acerto_lancamento_devolucao(
    analise_lancamento_receita_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,

):
    return baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_receita_prestacao_conta_2020_1,
        tipo_acerto=tipo_acerto_lancamento_devolucao,
        devolucao_ao_tesouro=None,
        detalhamento="teste"
    )

@pytest.fixture
def tipo_devolucao_ao_tesouro_teste():
    return baker.make('TipoDevolucaoAoTesouro', id='20', nome='Teste tipo devolução')

@pytest.fixture
def devolucao_ao_tesouro_parcial(prestacao_conta_2020_1_conciliada, tipo_devolucao_ao_tesouro_teste, despesa_no_periodo):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo=tipo_devolucao_ao_tesouro_teste,
        data=date(2020, 6, 6),
        despesa=despesa_no_periodo,
        valor=100.00,
        motivo='Motivo devolucao parcial teste',
        devolucao_total=False,
    )

@pytest.fixture
def solicitacao_devolucao_ao_tesouro(
    solicitacao_acerto_lancamento_devolucao,
    tipo_devolucao_ao_tesouro_teste,
):
    return baker.make(
        'SolicitacaoDevolucaoAoTesouro',
        solicitacao_acerto_lancamento=solicitacao_acerto_lancamento_devolucao,
        tipo=tipo_devolucao_ao_tesouro_teste,
        devolucao_total=False,
        valor=100.00,
        motivo='teste',
    )

@pytest.fixture
def queryset_ordered(rateio_despesa_01, rateio_despesa_02, devolucao_ao_tesouro_parcial, solicitacao_devolucao_ao_tesouro):
    return SolicitacaoDevolucaoAoTesouro.objects.all().order_by('criado_em')