import pytest
import datetime

from datetime import date

from model_bakery import baker
from sme_ptrf_apps.core.models.devolucao_ao_tesouro import DevolucaoAoTesouro

from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CUSTEIO

pytestmark = pytest.mark.django_db

@pytest.fixture
def prestacao_conta_em_analise(periodo, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        data_recebimento=date(2020, 10, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )

@pytest.fixture
def outra_prestacao_conta_em_analise(periodo, outra_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        data_recebimento=date(2020, 8, 1),
        status=PrestacaoConta.STATUS_EM_ANALISE
    )

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Tipo devolução 1', id=10)

@pytest.fixture
def outro_tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Tipo devolução 2', id=11)

@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        id=10,
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
        documento_transacao=12345
    )

@pytest.fixture
def tipo_aplicacao_recurso():
    return APLICACAO_CUSTEIO

@pytest.fixture
def especificacao_material_servico(tipo_aplicacao_recurso, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
    )

@pytest.fixture
def outra_especificacao_material_servico(tipo_aplicacao_recurso, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material de construção',
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
    )

@pytest.fixture
def primeiro_rateio(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
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
        valor_rateio=20.00,
        valor_original=10.00
    )

@pytest.fixture
def segundo_rateio(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
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
        valor_rateio=80.00,
        valor_original=70.00
    )

@pytest.fixture
def outra_despesa(outra_associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        id=11,
        associacao=outra_associacao,
        numero_documento='123456',
        data_documento=date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=200.00,
        documento_transacao=6789
    )

@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta_em_analise, tipo_devolucao_ao_tesouro, despesa, primeiro_rateio, segundo_rateio):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta_em_analise,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='Motivo teste 1',
        criado_em=datetime.date(2020, 1, 1)
    )

@pytest.fixture
def outra_devolucao_ao_tesouro(outra_prestacao_conta_em_analise, outro_tipo_devolucao_ao_tesouro, outra_despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=outra_prestacao_conta_em_analise,
        tipo=outro_tipo_devolucao_ao_tesouro,
        data=date(2020, 5, 1),
        despesa=outra_despesa,
        devolucao_total=False,
        valor=50.00,
        motivo='Motivo teste 2',
        criado_em=datetime.date(2021, 1, 1)
    )

@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )

@pytest.fixture
def queryset_ordered(devolucao_ao_tesouro, outra_devolucao_ao_tesouro):
    return DevolucaoAoTesouro.objects.all().order_by('criado_em')