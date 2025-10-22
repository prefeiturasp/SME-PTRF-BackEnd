import pytest
from model_bakery import baker

from ...api.serializers import AnalisePrestacaoContaRetrieveSerializer

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
    monkeypatch,
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

    monkeypatch.setattr(
        analise.__class__,
        'contas_pendencia_conciliacao_sem_solicitacao_de_acerto_em_conta',
        lambda self: [conta_associacao_cheque],
    )

    contas = analise.contas_solicitacoes_lancar_credito_ou_despesa()
    assert {conta.id for conta in contas} == {
        conta_associacao_cheque.id,
        conta_associacao_cartao.id,
    }
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa() is True

    contas_com_pendencia = analise.contas_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao()
    assert contas_com_pendencia == [conta_associacao_cheque]
    assert analise.tem_solicitacoes_lancar_credito_ou_despesa_com_pendencia_conciliacao() is True
