import pytest
from unittest.mock import patch
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.paa.models import AtaPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao import (
    gerar_ata_paa_retificacao_async,
    MAX_RETRIES,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def ata_paa_retificacao(paa_factory, periodo_paa_1, associacao, ata_paa_factory):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_1,
        associacao=associacao,
        status=PaaStatusEnum.EM_RETIFICACAO.name,
    )
    return ata_paa_factory.create(
        paa=paa,
        tipo_ata=AtaPaa.ATA_RETIFICACAO,
        status_geracao_pdf=AtaPaa.STATUS_NAO_GERADO,
    )


def test_gerar_ata_paa_retificacao_async_sucesso(ata_paa_retificacao):
    """Task deve completar com sucesso quando gerar_arquivo_ata_paa_retificacao retorna a ata."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=ata_paa_retificacao,
    ) as mock_gerar:
        result = gerar_ata_paa_retificacao_async.apply(args=[str(ata_paa_retificacao.uuid)])

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa_retificacao, usuario=None)


def test_gerar_ata_paa_retificacao_async_sem_username_passa_usuario_none(ata_paa_retificacao):
    """usuario deve ser None quando username não é fornecido."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=ata_paa_retificacao,
    ) as mock_gerar:
        result = gerar_ata_paa_retificacao_async.apply(args=[str(ata_paa_retificacao.uuid), ''])

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa_retificacao, usuario=None)


def test_gerar_ata_paa_retificacao_async_com_usuario(ata_paa_retificacao, usuario_task):
    """Task deve buscar o usuário pelo username e passá-lo ao service."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=ata_paa_retificacao,
    ) as mock_gerar:
        result = gerar_ata_paa_retificacao_async.apply(
            args=[str(ata_paa_retificacao.uuid), usuario_task.username]
        )

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa_retificacao, usuario=usuario_task)


def test_gerar_ata_paa_retificacao_async_chama_service_com_ata_correta(ata_paa_retificacao):
    """O service deve ser chamado com a instância de AtaPaa correspondente ao uuid informado."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=ata_paa_retificacao,
    ) as mock_gerar:
        gerar_ata_paa_retificacao_async.apply(args=[str(ata_paa_retificacao.uuid)])

    _, kwargs = mock_gerar.call_args
    assert kwargs['ata_paa'].uuid == ata_paa_retificacao.uuid


def test_gerar_ata_paa_retificacao_async_falha_quando_arquivo_retorna_none(ata_paa_retificacao):
    """Task deve falhar quando gerar_arquivo_ata_paa_retificacao retorna None."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=None,
    ):
        result = gerar_ata_paa_retificacao_async.apply(
            args=[str(ata_paa_retificacao.uuid)],
            retries=MAX_RETRIES,
        )

    assert result.failed()


def test_gerar_ata_paa_retificacao_async_falha_quando_ata_nao_encontrada():
    """Task deve falhar quando AtaPaa com o uuid informado não existe no banco."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_ata_paa_retificacao_async.apply(
        args=[uuid_invalido],
        retries=MAX_RETRIES,
    )

    assert result.failed()


def test_gerar_ata_paa_retificacao_async_max_retries_excedido_levanta_max_retries_error(ata_paa_retificacao):
    """MaxRetriesExceededError deve ser levantado quando todas as tentativas são esgotadas."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa_retificacao.gerar_arquivo_ata_paa_retificacao',
        return_value=None,
    ):
        result = gerar_ata_paa_retificacao_async.apply(
            args=[str(ata_paa_retificacao.uuid)],
            retries=MAX_RETRIES,
        )

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)


def test_gerar_ata_paa_retificacao_async_max_retries_excedido_com_ata_nao_encontrada():
    """MaxRetriesExceededError deve ser levantado quando a ata não existe e tentativas se esgotam."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_ata_paa_retificacao_async.apply(
        args=[uuid_invalido],
        retries=MAX_RETRIES,
    )

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)
