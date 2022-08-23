import pytest

from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta
from sme_ptrf_apps.core.services import AnaliseLancamentoPrestacaoContaService
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_service_limpar_status(analise_lancamento_realizado_service_01, analise_lancamento_realizado_service_02):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_lancamento_realizado_service_01.uuid}",
        f"{analise_lancamento_realizado_service_02.uuid}"
    ]

    result = AnaliseLancamentoPrestacaoContaService.limpar_status(
        uuids_analises_lancamentos=uuids_analises
    )

    analise_1 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_realizado_service_01.uuid)
    analise_2 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_realizado_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
    assert analise_1.justificativa is None
    assert analise_2.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE
    assert analise_2.justificativa is None


def test_service_limpar_status_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de lancamento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = [
    ]

    result = AnaliseLancamentoPrestacaoContaService.limpar_status(
        uuids_analises_lancamentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_limpar_status_pendente(analise_lancamento_pendente_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao pendente não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_lancamento_pendente_service_01.uuid}"
    ]

    result = AnaliseLancamentoPrestacaoContaService.limpar_status(
        uuids_analises_lancamentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_marcar_realizado(analise_lancamento_pendente_service_01, analise_lancamento_pendente_service_02):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_lancamento_pendente_service_01.uuid}",
        f"{analise_lancamento_pendente_service_02.uuid}"
    ]

    result = AnaliseLancamentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_lancamentos=uuids_analises
    )

    analise_1 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_pendente_service_01.uuid)
    analise_2 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_pendente_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO
    assert analise_1.justificativa is None
    assert analise_2.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO
    assert analise_2.justificativa is None


def test_service_marcar_realizado_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de lancamento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = [
    ]

    result = AnaliseLancamentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_lancamentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_marcar_realizado_status_realizado(analise_lancamento_realizado_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao realizado não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_lancamento_realizado_service_01.uuid}"
    ]

    result = AnaliseLancamentoPrestacaoContaService.marcar_como_realizado(
        uuids_analises_lancamentos=uuids_analises
    )

    assert resultado_esperado == result


def test_service_justificar_nao_realizado(
    analise_lancamento_pendente_service_01,
    analise_lancamento_pendente_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_analises = [
        f"{analise_lancamento_pendente_service_01.uuid}",
        f"{analise_lancamento_pendente_service_02.uuid}"
    ]

    justificativa = "justificativa teste"

    result = AnaliseLancamentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_lancamentos=uuids_analises,
        justificativa=justificativa
    )

    analise_1 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_pendente_service_01.uuid)
    analise_2 = AnaliseLancamentoPrestacaoConta.by_uuid(analise_lancamento_pendente_service_02.uuid)

    assert resultado_esperado == result
    assert analise_1.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO
    assert analise_1.justificativa == justificativa
    assert analise_2.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO
    assert analise_2.justificativa == justificativa


def test_service_justificar_nao_realizado_sem_uuid_analise():
    resultado_esperado = {
        "mensagem": "É necessário enviar pelo menos um uuid da analise de lancamento.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "parametros_requeridos"
    }

    uuids_analises = []
    justificativa = "teste"

    result = AnaliseLancamentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_lancamentos=uuids_analises,
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

    result = AnaliseLancamentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_lancamentos=uuids_analises,
        justificativa=justificativa
    )

    assert resultado_esperado == result


def test_service_justificar_nao_realizado_status_justificado(analise_lancamento_justificado_service_01):
    resultado_esperado = {
        "mensagem": "Status realizacao justificado não é aceito nessa ação.",
        "status": status.HTTP_400_BAD_REQUEST,
        "erro": "Status invalido."
    }

    uuids_analises = [
        f"{analise_lancamento_justificado_service_01.uuid}"
    ]
    justificativa = "teste"

    result = AnaliseLancamentoPrestacaoContaService.justificar_nao_realizacao(
        uuids_analises_lancamentos=uuids_analises,
        justificativa=justificativa
    )

    assert resultado_esperado == result


def test_marcar_devolucao_tesouro_atualizada(
    analise_lancamento_despesa_prestacao_conta_2020_1,
    tipo_acerto_lancamento_devolucao,
    devolucao_ao_tesouro_parcial,
    solicitacao_acerto_lancamento_devolucao
):
    assert not analise_lancamento_despesa_prestacao_conta_2020_1.devolucao_tesouro_atualizada

    result = AnaliseLancamentoPrestacaoContaService.marcar_devolucao_tesouro_como_atualizada(
        analise_lancamento_despesa_prestacao_conta_2020_1
    )

    assert result.devolucao_tesouro_atualizada
