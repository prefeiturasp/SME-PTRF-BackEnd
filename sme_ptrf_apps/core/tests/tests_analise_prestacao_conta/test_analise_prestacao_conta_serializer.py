import pytest
from model_bakery import baker

from ...api.serializers import AnalisePrestacaoContaRetrieveSerializer
from ...models import TipoAcertoLancamento

pytestmark = pytest.mark.django_db


def test_retrieve_serializer(analise_prestacao_conta_2020_1):
    serializer = AnalisePrestacaoContaRetrieveSerializer(analise_prestacao_conta_2020_1)
    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['id']
    assert serializer.data['prestacao_conta']
    assert serializer.data['devolucao_prestacao_conta']
    assert serializer.data['status']
    assert serializer.data['criado_em']
    assert serializer.data['versao']
    assert serializer.data['versao_pdf_apresentacao_apos_acertos']


def test_contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao(
    analise_prestacao_conta_2020_1,
    conta_associacao_cheque,
    conta_associacao_cartao,
    tipo_acerto_documento_requer_inclusao_credito,
    tipo_acerto_documento_requer_inclusao_despesa,
):
    analise = analise_prestacao_conta_2020_1

    analise_documento_credito = baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise,
        conta_associacao=conta_associacao_cheque,
    )
    baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_credito,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_credito,
    )

    analise_documento_gasto = baker.make(
        'AnaliseDocumentoPrestacaoConta',
        analise_prestacao_conta=analise,
        conta_associacao=conta_associacao_cartao,
    )
    baker.make(
        'SolicitacaoAcertoDocumento',
        analise_documento=analise_documento_gasto,
        tipo_acerto=tipo_acerto_documento_requer_inclusao_despesa,
    )

    contas = analise.contas_solicitacoes_lancar_credito_ou_despesa()
    assert {conta.id for conta in contas} == {
        conta_associacao_cheque.id,
        conta_associacao_cartao.id,
    }
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa() is True

    contas_com_pendencia = analise.contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao()
    assert {conta.id for conta in contas_com_pendencia} == {
        conta_associacao_cheque.id,
        conta_associacao_cartao.id,
    }
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao() is True

    baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise,
        prestacao_conta=analise.prestacao_conta,
        conta_associacao=conta_associacao_cartao,
        saldo_extrato=10,
    )

    contas_filtradas = analise.contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao()
    assert [conta.id for conta in contas_filtradas] == [conta_associacao_cheque.id]
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao() is True


def test_contas_solicitacoes_lancar_credito_ou_despesa_para_lancamentos(
    analise_prestacao_conta_2020_1,
    analise_lancamento_receita_prestacao_conta_2020_1,
):
    analise = analise_prestacao_conta_2020_1
    analise_lancamento = analise_lancamento_receita_prestacao_conta_2020_1
    conta = analise_lancamento.receita.conta_associacao

    tipo_lancar_credito = baker.make(
        'TipoAcertoLancamento',
        nome='Lancar credito',
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
    )

    baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_lancar_credito,
    )

    contas = analise.contas_solicitacoes_lancar_credito_ou_despesa()
    assert [conta.id for conta in contas] == [conta.id]

    analise_exclusao = baker.make(
        'AnalisePrestacaoConta',
        prestacao_conta=analise.prestacao_conta,
    )
    analise_lancamento_exclusao = baker.make(
        'AnaliseLancamentoPrestacaoConta',
        analise_prestacao_conta=analise_exclusao,
        receita=analise_lancamento.receita,
    )
    tipo_exclusao = baker.make(
        'TipoAcertoLancamento',
        nome='Exclusao de lancamento',
        categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
    )
    baker.make(
        'SolicitacaoAcertoLancamento',
        analise_lancamento=analise_lancamento_exclusao,
        tipo_acerto=tipo_exclusao,
    )

    contas_exclusao = analise_exclusao.contas_solicitacoes_lancar_credito_ou_despesa()
    assert [c.id for c in contas_exclusao] == [conta.id]

    baker.make(
        'AnaliseContaPrestacaoConta',
        analise_prestacao_conta=analise,
        prestacao_conta=analise.prestacao_conta,
        conta_associacao=conta,
        saldo_extrato=100,
    )

    assert analise.contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao() == []
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao() is False
