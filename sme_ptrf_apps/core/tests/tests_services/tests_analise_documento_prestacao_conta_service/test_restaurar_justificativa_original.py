import pytest

from rest_framework import status

from sme_ptrf_apps.core.models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db


def test_restaurar_justificativa_original(
    observacao_conciliacao_teste_service_02,
    solicitacao_acerto_documento_edicao_informacao_teste_service
):
    from sme_ptrf_apps.core.services import SolicitacaoAcertoDocumentoService

    uuid_solicitacao_acerto = f"{solicitacao_acerto_documento_edicao_informacao_teste_service.uuid}"

    response = SolicitacaoAcertoDocumentoService.reataurar_justificativa_original(
        uuid_solicitacao_acerto=uuid_solicitacao_acerto,
    )

    analise_documento = solicitacao_acerto_documento_edicao_informacao_teste_service.analise_documento

    conta_associacao = analise_documento.conta_associacao
    periodo = analise_documento.analise_prestacao_conta.prestacao_conta.periodo
    associacao = analise_documento.analise_prestacao_conta.prestacao_conta.associacao

    observacao = ObservacaoConciliacao.objects.filter(
        periodo=periodo,
        conta_associacao=conta_associacao,
        associacao=associacao,
    ).first()

    resposta_esperada = {
        "mensagem": "Restaurar justificativa original realizada com sucesso.",
        "status": status.HTTP_200_OK
    }

    assert not analise_documento.informacao_conciliacao_atualizada
    assert observacao.texto == observacao.justificativa_original
    assert response == resposta_esperada
