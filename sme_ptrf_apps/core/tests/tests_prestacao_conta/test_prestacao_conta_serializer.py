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
        data_retorno_ue=None
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
def despesa(despesa_factory, associacao, tipo_documento, tipo_transacao):
    return despesa_factory(
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
    assert serializer.data['analises_de_conta_da_prestacao'] == []
    assert serializer.data['motivos_aprovacao_ressalva']
    assert serializer.data['outros_motivos_aprovacao_ressalva']
    assert serializer.data['motivos_reprovacao']
    assert serializer.data['outros_motivos_reprovacao']
    assert serializer.data['recomendacoes']
    assert serializer.data['devolucoes_ao_tesouro_da_prestacao']
    assert serializer.data['analise_atual'] is None
    assert serializer.data['justificativa_pendencia_realizacao']
    assert serializer.data['ata_aprensentacao_gerada'] == False


def test_retrieve_serializer_with_solicitacoes_lancar_credito_ou_despesa(
    prestacao_conta,
    conta_associacao_cheque,
    tipo_acerto_documento_requer_inclusao_credito,
    monkeypatch,
):
    monkeypatch.setattr(
        prestacao_conta.associacao,
        'pendencias_conciliacao_bancaria_por_periodo_para_geracao_de_documentos',
        lambda periodo: []
    )
    analise = baker.make('AnalisePrestacaoConta', prestacao_conta=prestacao_conta)
    analise_documento = baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise,
        conta_associacao=conta_associacao_cheque,
    )
    baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_credito,
    )
    baker.make(
        'ObservacaoConciliacao',
        periodo=prestacao_conta.periodo,
        conta_associacao=conta_associacao_cheque,
        associacao=prestacao_conta.associacao,
        texto='Justificativa registrada',
    )

    prestacao_conta.analise_atual = analise
    prestacao_conta.save(update_fields=['analise_atual'])

    serializer = PrestacaoContaRetrieveSerializer(prestacao_conta)
    analise_data = serializer.data['analise_atual']

    assert analise_data is not None
    assert analise_data['solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao'] is True
    assert analise_data['contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao'] == [
        str(conta_associacao_cheque.uuid)
    ]
    assert analise_data['solicitar_correcao_de_justificativa_de_conciliacao'] is False
    assert analise_data['contas_solicitar_correcao_de_justificativa_de_conciliacao'] == []


def test_retrieve_serializer_sem_justificativa(
    prestacao_conta,
    conta_associacao_cheque,
    monkeypatch,
):
    monkeypatch.setattr(
        prestacao_conta.associacao,
        'pendencias_conciliacao_bancaria_por_periodo_para_geracao_de_documentos',
        lambda periodo: [{
            'conta': conta_associacao_cheque,
            'observacao': False,
            'extrato': False,
            'justificativa': True,
        }]
    )
    analise = baker.make('AnalisePrestacaoConta', prestacao_conta=prestacao_conta)
    baker.make(
        'ObservacaoConciliacao',
        periodo=prestacao_conta.periodo,
        conta_associacao=conta_associacao_cheque,
        associacao=prestacao_conta.associacao,
        texto='',
    )

    prestacao_conta.analise_atual = analise
    prestacao_conta.save(update_fields=['analise_atual'])

    serializer = PrestacaoContaRetrieveSerializer(prestacao_conta)
    analise_data = serializer.data['analise_atual']

    assert analise_data['solicitar_correcao_de_justificativa_de_conciliacao'] is True
    assert analise_data['contas_solicitar_correcao_de_justificativa_de_conciliacao'] == [
        str(conta_associacao_cheque.uuid)
    ]


def test_retrieve_serializer_sem_justificativa_ja_solicitada(
    prestacao_conta,
    conta_associacao_cheque,
    monkeypatch,
):
    monkeypatch.setattr(
        prestacao_conta.associacao,
        'pendencias_conciliacao_bancaria_por_periodo_para_geracao_de_documentos',
        lambda periodo: [{
            'conta': conta_associacao_cheque,
            'observacao': False,
            'extrato': False,
            'justificativa': True,
        }]
    )
    analise = baker.make('AnalisePrestacaoConta', prestacao_conta=prestacao_conta)
    baker.make(
        'ObservacaoConciliacao',
        periodo=prestacao_conta.periodo,
        conta_associacao=conta_associacao_cheque,
        associacao=prestacao_conta.associacao,
        texto=None,
    )
    baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise,
        prestacao_conta=prestacao_conta,
        conta_associacao=conta_associacao_cheque,
        solicitar_correcao_de_justificativa_de_conciliacao=True,
    )

    prestacao_conta.analise_atual = analise
    prestacao_conta.save(update_fields=['analise_atual'])

    serializer = PrestacaoContaRetrieveSerializer(prestacao_conta)
    analise_data = serializer.data['analise_atual']

    assert analise_data['solicitar_correcao_de_justificativa_de_conciliacao'] is False
    assert analise_data['contas_solicitar_correcao_de_justificativa_de_conciliacao'] == []
