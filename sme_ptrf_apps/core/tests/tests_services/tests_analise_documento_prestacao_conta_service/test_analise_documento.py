import pytest

from sme_ptrf_apps.core.models import AnaliseDocumentoPrestacaoConta
from sme_ptrf_apps.core.services import AnaliseDocumentoPrestacaoContaService
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_service_limpar_status(analise_documento_realizado_service_01, analise_documento_realizado_service_02):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_documento_realizado_service_01.uuid}",
        f"{analise_documento_realizado_service_02.uuid}"
    ]

    result = AnaliseDocumentoPrestacaoContaService.limpar_status(
        uuids_analises_documentos=uuids_analises
    )

    analise_1 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_realizado_service_01.uuid)
    analise_2 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_realizado_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
    assert analise_1.justificativa is None
    assert analise_2.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
    assert analise_2.justificativa is None


def test_service_limpar_status_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de documento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = [
    ]

    result = AnaliseDocumentoPrestacaoContaService.limpar_status(
        uuids_analises_documentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_limpar_status_pendente(analise_documento_pendente_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao pendente não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_documento_pendente_service_01.uuid}"
    ]

    result = AnaliseDocumentoPrestacaoContaService.limpar_status(
        uuids_analises_documentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_marcar_realizado(analise_documento_pendente_service_01, analise_documento_pendente_service_02):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_documento_pendente_service_01.uuid}",
        f"{analise_documento_pendente_service_02.uuid}"
    ]

    result = AnaliseDocumentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_documentos=uuids_analises
    )

    analise_1 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_pendente_service_01.uuid)
    analise_2 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_pendente_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO
    assert analise_1.justificativa is None
    assert analise_2.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO
    assert analise_2.justificativa is None


def test_service_marcar_realizado_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de documento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = [
    ]

    result = AnaliseDocumentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_documentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_marcar_realizado_status_realizado(analise_documento_realizado_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao realizado não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_documento_realizado_service_01.uuid}"
    ]

    result = AnaliseDocumentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_documentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_justificar_nao_realizado(
    analise_documento_pendente_service_01,
    analise_documento_pendente_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_documento_pendente_service_01.uuid}",
        f"{analise_documento_pendente_service_02.uuid}"
    ]

    justificativa = "justificativa teste"

    result = AnaliseDocumentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_documentos=uuids_analises,
        justificativa=justificativa
    )

    analise_1 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_pendente_service_01.uuid)
    analise_2 = AnaliseDocumentoPrestacaoConta.by_uuid(analise_documento_pendente_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO
    assert analise_1.justificativa == justificativa
    assert analise_2.status_realizacao == AnaliseDocumentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO
    assert analise_2.justificativa == justificativa


def test_service_justificar_nao_realizado_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de documento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = []
    justificativa = "teste"

    result = AnaliseDocumentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_documentos=uuids_analises,
        justificativa=justificativa
    )

    assert resultado_esperado == result


def test_service_justificar_nao_realizado_sem_justificativa():
    resultado_esperado = {
        "mensagem": "É necessário enviar a justificativa de não realizacação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = []
    justificativa = None

    result = AnaliseDocumentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_documentos=uuids_analises,
        justificativa=justificativa
    )

    assert resultado_esperado == result


def test_service_justificar_nao_realizado_status_justificado(analise_documento_justificado_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao justificado não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_documento_justificado_service_01.uuid}"
    ]
    justificativa = "teste"

    result = AnaliseDocumentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_documentos=uuids_analises,
        justificativa=justificativa
    )

    assert resultado_esperado == result


def test_service_marcar_como_credito_incluido(analise_documento_justificado_service_01, receita_100_no_periodo):
    resultado_esperado = {
        "mensagem": "Crédito incluído atualizado com sucesso.",
        "status": status.HTTP_200_OK,
    }

    result = AnaliseDocumentoPrestacaoContaService.marcar_como_credito_incluido(
        uuid_analise_documento=analise_documento_justificado_service_01.uuid,
        uuid_credito_incluido=receita_100_no_periodo.uuid
    )

    assert result == resultado_esperado
