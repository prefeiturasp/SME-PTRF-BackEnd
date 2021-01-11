import pytest
from datetime import date

from model_bakery import baker

from ...api.serializers.prestacao_conta_serializer import (PrestacaoContaLookUpSerializer, PrestacaoContaListSerializer,
                                                           PrestacaoContaRetrieveSerializer)

pytestmark = pytest.mark.django_db


def test_lookup_serializer(prestacao_conta):
    serializer = PrestacaoContaLookUpSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['periodo_uuid']
    assert serializer.data['status']


@pytest.fixture
def tecnico_dre(dre):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='José Testando',
        rf='271170',
    )


@pytest.fixture
def atribuicao(tecnico_dre, unidade, periodo):
    return baker.make(
        'Atribuicao',
        tecnico=tecnico_dre,
        unidade=unidade,
        periodo=periodo,
    )


@pytest.fixture
def processo_associacao_2019(associacao):
    return baker.make(
        'ProcessoAssociacao',
        associacao=associacao,
        numero_processo='123456',
        ano='2019'
    )


def test_list_serializer(prestacao_conta, atribuicao, processo_associacao_2019):
    serializer = PrestacaoContaListSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['unidade_eol']
    assert serializer.data['unidade_nome']
    assert serializer.data['status']
    assert serializer.data['tecnico_responsavel'] == atribuicao.tecnico.nome
    assert serializer.data['processo_sei'] == processo_associacao_2019.numero_processo
    assert serializer.data['data_recebimento']
    assert serializer.data['data_ultima_analise']
    assert serializer.data['devolucao_ao_tesouro']


@pytest.fixture
def devolucao_prestacao_conta_2020_1(prestacao_conta):
    return baker.make(
        'DevolucaoPrestacaoConta',
        prestacao_conta=prestacao_conta,
        data=date(2020, 7, 1),
        data_limite_ue=date(2020, 8, 1),
    )


@pytest.fixture
def _analise_conta_prestacao_conta_2020_1(prestacao_conta, conta_associacao_cheque):
    return baker.make(
        'AnaliseContaPrestacaoConta',
        prestacao_conta=prestacao_conta,
        conta_associacao=conta_associacao_cheque,
        data_extrato=date(2020, 7, 1),
        saldo_extrato=100.00,
    )


@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=date(2020, 3, 10),
        valor_total=100.00,
    )

@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


@pytest.fixture
def devolucao_ao_tesouro(prestacao_conta, tipo_devolucao_ao_tesouro, despesa):
    return baker.make(
        'DevolucaoAoTesouro',
        prestacao_conta=prestacao_conta,
        tipo=tipo_devolucao_ao_tesouro,
        data=date(2020, 7, 1),
        despesa=despesa,
        devolucao_total=True,
        valor=100.00,
        motivo='teste'
    )

def test_retrieve_serializer(prestacao_conta, devolucao_prestacao_conta_2020_1, atribuicao, processo_associacao_2019,
                             _analise_conta_prestacao_conta_2020_1, devolucao_ao_tesouro):
    serializer = PrestacaoContaRetrieveSerializer(prestacao_conta)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['periodo_uuid']
    assert serializer.data['status']
    assert serializer.data['associacao']
    assert serializer.data['tecnico_responsavel']
    assert serializer.data['data_recebimento']
    assert serializer.data['devolucoes_da_prestacao']
    assert serializer.data['processo_sei'] == processo_associacao_2019.numero_processo
    assert serializer.data['data_ultima_analise']
    assert serializer.data['devolucao_ao_tesouro']
    assert serializer.data['analises_de_conta_da_prestacao']
    assert serializer.data['motivo_aprovacao_ressalva']
    assert serializer.data['motivos_reprovacao']
    assert serializer.data['devolucoes_ao_tesouro_da_prestacao']
