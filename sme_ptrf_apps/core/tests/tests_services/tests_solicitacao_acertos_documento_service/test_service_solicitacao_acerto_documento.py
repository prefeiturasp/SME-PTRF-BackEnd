import pytest

from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento
from sme_ptrf_apps.core.services import SolicitacaoAcertoDocumentoService
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_service_limpar_status(
    solicitacao_acerto_documento_realizado_service_01,
    solicitacao_acerto_documento_realizado_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_realizado_service_01.uuid}",
        f"{solicitacao_acerto_documento_realizado_service_02.uuid}"
    ]

    result = SolicitacaoAcertoDocumentoService.limpar_status(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(solicitacao_acerto_documento_realizado_service_01.uuid)
    solicitacao_2 = SolicitacaoAcertoDocumento.by_uuid(solicitacao_acerto_documento_realizado_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa is None
    assert solicitacao_2.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_2.justificativa is None
    assert resultado_esperado == result


def test_service_justificar_nao_realizado(
    solicitacao_acerto_documento_pendente_service_01,
    solicitacao_acerto_documento_pendente_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_01.uuid}",
        f"{solicitacao_acerto_documento_pendente_service_02.uuid}"
    ]

    justificativa = "justificativa teste"

    result = SolicitacaoAcertoDocumentoService.justificar_nao_realizacao(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes,
        justificativa=justificativa
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(solicitacao_acerto_documento_pendente_service_01.uuid)
    solicitacao_2 = SolicitacaoAcertoDocumento.by_uuid(solicitacao_acerto_documento_pendente_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_JUSTIFICADO
    assert solicitacao_1.justificativa == justificativa
    assert solicitacao_2.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_JUSTIFICADO
    assert solicitacao_2.justificativa == justificativa
    assert resultado_esperado == result


def test_marcar_como_esclarecido(
    solicitacao_acerto_documento_realizado_service_01
):
    assert solicitacao_acerto_documento_realizado_service_01.esclarecimentos is None

    uuid_solicitacao = f"{solicitacao_acerto_documento_realizado_service_01.uuid}"
    result = SolicitacaoAcertoDocumentoService.marcar_como_esclarecido(
        uuid_solicitacao_acerto=uuid_solicitacao,
        esclarecimento="Este é o esclarecimento"
    )

    solicitacao_acerto = SolicitacaoAcertoDocumento.by_uuid(uuid_solicitacao)
    resultado_esperado = {
        "mensagem": "Esclarecimento atualizado com sucesso.",
        "status": status.HTTP_200_OK,
    }

    assert solicitacao_acerto.esclarecimentos
    assert solicitacao_acerto.esclarecimentos == 'Este é o esclarecimento'
    assert result == resultado_esperado


def test_service_marcar_realizado_categoria_inclusao_credito_ajuste_realizado(
    solicitacao_acerto_documento_pendente_service_01
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_01.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_01.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_inclusao_credito_ajuste_nao_realizado(
    solicitacao_acerto_documento_pendente_service_02
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_02.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_inclusao_gasto_ajuste_realizado(
    solicitacao_acerto_documento_pendente_service_03
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_03.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_03.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_inclusao_gasto_ajuste_nao_realizado(
    solicitacao_acerto_documento_pendente_service_04
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_04.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_04.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_solicitacao_esclarecimento_ajuste_realizado(
    solicitacao_acerto_documento_pendente_service_05
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_05.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_05.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_solicitacao_esclarecimento_ajuste_nao_realizado(
    solicitacao_acerto_documento_pendente_service_06
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_documento_pendente_service_06.uuid}",
    ]

    result = SolicitacaoAcertoDocumentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_documentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoDocumento.by_uuid(
        solicitacao_acerto_documento_pendente_service_06.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result
