import pytest

from rest_framework import status

from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta, ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_service_editar_informacao_conciliacao(
    analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service,
    observacao_conciliacao_teste_service
):
    from sme_ptrf_apps.core.services import SolicitacaoAcertoDocumentoService

    uuid_analise_documento = f"{analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service.uuid}"

    conta_associacao = analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service.conta_associacao
    periodo = analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service.analise_prestacao_conta.prestacao_conta.periodo
    associacao = analise_documento_prestacao_conta_demonstativo_financeiro_edicao_informacao_teste_service.analise_prestacao_conta.prestacao_conta.associacao

    response = SolicitacaoAcertoDocumentoService.editar_informacao_conciliacao(
        uuid_analise_documento=uuid_analise_documento,
        justificativa_conciliacao='Esta será a nova justificativa alterada'
    )

    analise_documento_editada = AnaliseDocumentoPrestacaoConta.by_uuid(uuid_analise_documento)

    observacao = ObservacaoConciliacao.objects.filter(
        periodo=periodo,
        conta_associacao=conta_associacao,
        associacao=associacao,
    ).first()

    resultado_esperado = {
        "mensagem": "Edição de informação da conciliação atualizada com sucesso.",
        "status": status.HTTP_200_OK
    }

    assert analise_documento_editada.informacao_conciliacao_atualizada
    assert observacao.texto == 'Esta será a nova justificativa alterada'
    assert response == resultado_esperado
