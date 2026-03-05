import pytest
from unittest.mock import patch
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.paa.tasks.gerar_ata_paa import gerar_ata_paa_async, MAX_RETRIES

pytestmark = pytest.mark.django_db


def test_gerar_ata_paa_async_sucesso(ata_paa):
    """Testa que a task completa com sucesso quando gerar_arquivo_ata_paa retorna a ata."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=ata_paa
    ) as mock_gerar:
        result = gerar_ata_paa_async.apply(args=[str(ata_paa.uuid)])

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa, usuario=None)


def test_gerar_ata_paa_async_sucesso_sem_username_passa_usuario_none(ata_paa):
    """Testa que usuario é None quando username não é fornecido."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=ata_paa
    ) as mock_gerar:
        result = gerar_ata_paa_async.apply(args=[str(ata_paa.uuid), ''])

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa, usuario=None)


def test_gerar_ata_paa_async_sucesso_com_usuario(ata_paa, usuario_task):
    """Testa que a task busca o usuário pelo username e o passa para o service."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=ata_paa
    ) as mock_gerar:
        result = gerar_ata_paa_async.apply(args=[str(ata_paa.uuid), usuario_task.username])

    assert result.successful()
    mock_gerar.assert_called_once_with(ata_paa=ata_paa, usuario=usuario_task)


def test_gerar_ata_paa_async_chama_service_com_ata_correta(ata_paa):
    """Testa que o service é chamado com a instância de AtaPaa correta."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=ata_paa
    ) as mock_gerar:
        gerar_ata_paa_async.apply(args=[str(ata_paa.uuid)])

    _, kwargs = mock_gerar.call_args
    assert kwargs['ata_paa'].uuid == ata_paa.uuid


def test_gerar_ata_paa_async_falha_quando_arquivo_retorna_none(ata_paa):
    """Testa que a task falha quando gerar_arquivo_ata_paa retorna None."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=None
    ):
        result = gerar_ata_paa_async.apply(args=[str(ata_paa.uuid)], retries=MAX_RETRIES)

    assert result.failed()


def test_gerar_ata_paa_async_falha_quando_ata_nao_encontrada():
    """Testa que a task falha quando AtaPaa com o UUID informado não existe."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_ata_paa_async.apply(args=[uuid_invalido], retries=MAX_RETRIES)

    assert result.failed()


def test_gerar_ata_paa_async_max_retries_excedido_levanta_max_retries_error(ata_paa):
    """Testa que MaxRetriesExceededError é levantado quando todas as tentativas são esgotadas."""
    with patch(
        'sme_ptrf_apps.paa.tasks.gerar_ata_paa.gerar_arquivo_ata_paa',
        return_value=None
    ):
        result = gerar_ata_paa_async.apply(args=[str(ata_paa.uuid)], retries=MAX_RETRIES)

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)


def test_gerar_ata_paa_async_max_retries_excedido_com_ata_nao_encontrada():
    """Testa que MaxRetriesExceededError é levantado quando a ata não existe e tentativas se esgotam."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_ata_paa_async.apply(args=[uuid_invalido], retries=MAX_RETRIES)

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)
