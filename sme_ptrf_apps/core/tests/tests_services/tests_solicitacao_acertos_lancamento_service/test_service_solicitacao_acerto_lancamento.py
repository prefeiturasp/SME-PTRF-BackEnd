import pytest

from sme_ptrf_apps.core.models import SolicitacaoAcertoLancamento
from sme_ptrf_apps.core.services import SolicitacaoAcertoLancamentoService
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_service_limpar_status(solicitacao_acerto_lancamento_realizado_service_01, solicitacao_acerto_lancamento_realizado_service_02):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_realizado_service_01.uuid}",
        f"{solicitacao_acerto_lancamento_realizado_service_02.uuid}"
    ]

    result = SolicitacaoAcertoLancamentoService.limpar_status(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(solicitacao_acerto_lancamento_realizado_service_01.uuid)
    solicitacao_2 = SolicitacaoAcertoLancamento.by_uuid(solicitacao_acerto_lancamento_realizado_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa is None
    assert solicitacao_2.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_2.justificativa is None
    assert resultado_esperado == result


def test_service_justificar_nao_realizado(
    solicitacao_acerto_lancamento_pendente_service_01,
    solicitacao_acerto_lancamento_pendente_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_service_01.uuid}",
        f"{solicitacao_acerto_lancamento_pendente_service_02.uuid}"
    ]

    justificativa = "justificativa teste"

    result = SolicitacaoAcertoLancamentoService.justificar_nao_realizacao(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes,
        justificativa=justificativa
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(solicitacao_acerto_lancamento_pendente_service_01.uuid)
    solicitacao_2 = SolicitacaoAcertoLancamento.by_uuid(solicitacao_acerto_lancamento_pendente_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO
    assert solicitacao_1.justificativa == justificativa
    assert solicitacao_2.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_JUSTIFICADO
    assert solicitacao_2.justificativa == justificativa
    assert resultado_esperado == result


def test_marcar_como_esclarecido(
    tipo_acerto_esclarecimento,
    solicitacao_acerto_esclarecimento
):
    assert solicitacao_acerto_esclarecimento.esclarecimentos is None

    uuid_solicitacao = f"{solicitacao_acerto_esclarecimento.uuid}"
    result = SolicitacaoAcertoLancamentoService.marcar_como_esclarecido(
        uuid_solicitacao_acerto=uuid_solicitacao,
        esclarecimento="Este é o esclarecimento"
    )

    solicitacao_acerto = SolicitacaoAcertoLancamento.by_uuid(uuid_solicitacao)
    resultado_esperado = {
        "mensagem": "Esclarecimento atualizado com sucesso.",
        "status": status.HTTP_200_OK,
    }

    assert solicitacao_acerto.esclarecimentos
    assert solicitacao_acerto.esclarecimentos == 'Este é o esclarecimento'
    assert result == resultado_esperado


def test_service_marcar_realizado_categoria_edicao_lancamento_ajuste_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_02.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_edicao_lancamento_ajuste_nao_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_01
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_01.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_edicao_lancamento_service_01.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_devolucao_ajuste_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_02.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_devolucao_ajuste_nao_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_01
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_01.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_devolucao_service_01.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_exclusao_lancamento_ajuste_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_02.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_exclusao_lancamento_ajuste_nao_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_01
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_01.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_exclusao_lancamento_service_01.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_solicitacao_esclarecimento_ajuste_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_02
):
    resultado_esperado = {
        "mensagem": "Status alterados com sucesso!",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": True,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_02.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_02.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO
    assert solicitacao_1.justificativa is None
    assert resultado_esperado == result


def test_service_marcar_realizado_categoria_solicitacao_esclarecimento_ajuste_nao_realizado(
    solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_01
):
    resultado_esperado = {
        "mensagem": "Não foi possível alterar o status da solicitação, pois os ajustes solicitados não foram realizados.",
        "status": status.HTTP_200_OK,
        "todas_as_solicitacoes_marcadas_como_realizado": False,
    }

    uuids_solicitacoes = [
        f"{solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_01.uuid}",
    ]

    result = SolicitacaoAcertoLancamentoService.marcar_como_realizado(
        uuids_solicitacoes_acertos_lancamentos=uuids_solicitacoes
    )

    solicitacao_1 = SolicitacaoAcertoLancamento.by_uuid(
        solicitacao_acerto_lancamento_pendente_categoria_solicitacao_esclarecimento_service_01.uuid)

    assert solicitacao_1.status_realizacao == SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE
    assert solicitacao_1.justificativa == "justificativa"
    assert resultado_esperado == result
