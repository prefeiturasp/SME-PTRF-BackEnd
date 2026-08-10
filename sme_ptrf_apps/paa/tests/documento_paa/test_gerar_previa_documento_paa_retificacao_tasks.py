import pytest
from unittest.mock import patch, ANY, MagicMock
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa_retificacao import (
    gerar_previa_documento_paa_retificacao_async,
    MAX_RETRIES,
)

pytestmark = pytest.mark.django_db

_SERVICE_PATH = 'sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa_retificacao.DocumentoPaaService'
_GERAR_PDF_PATH = 'sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa_retificacao.gerar_arquivo_documento_paa_pdf'
_RETIFICACAO_SERVICE_PATH = 'sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa_retificacao.RetificacaoPaaService'


def test_gerar_previa_retificacao_async_sucesso(paa, usuario_task):
    """Testa que a task completa com sucesso chamando os métodos corretos do service."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {
            'prioridades': {'uuid-1': {'acao': 'modificado'}}
        }

        result = gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username]
        )

    assert result.successful()
    mock_service_class.return_value.preparar_documento_para_task.assert_called_once()
    mock_service_class.return_value.iniciar.assert_not_called()
    mock_service_class.return_value.marcar_concluido.assert_called_once()
    mock_service_class.return_value.marcar_erro.assert_not_called()


def test_gerar_previa_retificacao_async_service_criado_com_retificacao_true(paa, usuario_task):
    """Testa que DocumentoPaaService é instanciado com retificacao=True e previa=True."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {'prioridades': {}}

        gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username]
        )

    mock_service_class.assert_called_once_with(
        paa=paa, usuario=usuario_task.username, previa=True, logger=ANY, retificacao=True
    )


def test_gerar_previa_retificacao_async_gerar_pdf_chamado_com_alteracoes(paa, usuario_task):
    """Testa que gerar_arquivo_documento_paa_pdf é chamado com alteracoes e previa=True."""
    alteracoes = {'prioridades': {'uuid-1': {'acao': 'modificado'}}}

    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH) as mock_gerar_pdf, \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = alteracoes

        gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username]
        )

    mock_service = mock_service_class.return_value
    mock_gerar_pdf.assert_called_once_with(
        paa, mock_service.documento_paa, usuario_task, previa=True, alteracoes=alteracoes,
        retificacao=True, px_versao=mock_service._calcular_proxima_versao_retificacao.return_value
    )


def test_gerar_previa_retificacao_async_falha_sem_alteracoes(paa, usuario_task):
    """Testa que a task falha quando identificar_alteracoes retorna vazio."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {}
        mock_service_class.return_value.documento_paa = MagicMock()

        result = gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    assert result.failed()
    mock_service_class.return_value.marcar_erro.assert_called()


def test_gerar_previa_retificacao_async_falha_gerar_pdf_chama_marcar_erro(paa, usuario_task):
    """Testa que service.marcar_erro() é chamado quando a geração do PDF falha."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH, side_effect=Exception("Erro ao gerar PDF")), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {
            'prioridades': {'uuid-1': {'acao': 'modificado'}}
        }
        mock_service_class.return_value.documento_paa = MagicMock()

        result = gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    assert result.failed()
    mock_service_class.return_value.marcar_erro.assert_called_once()


def test_gerar_previa_retificacao_async_falha_max_retries_excedido(paa, usuario_task):
    """Testa que MaxRetriesExceededError é levantado quando as tentativas são esgotadas."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH, side_effect=Exception("Erro ao gerar PDF")), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {
            'prioridades': {'uuid-1': {'acao': 'modificado'}}
        }
        mock_service_class.return_value.documento_paa = MagicMock()

        result = gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)


def test_gerar_previa_retificacao_async_falha_quando_paa_nao_encontrado():
    """Testa que a task falha quando Paa com o UUID informado não existe."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_previa_documento_paa_retificacao_async.apply(
        args=[uuid_invalido, 'qualquer_usuario'],
        retries=MAX_RETRIES
    )

    assert result.failed()


def test_gerar_previa_retificacao_async_marcar_erro_nao_chamado_quando_documento_paa_none(paa, usuario_task):
    """Testa que marcar_erro() não é chamado quando documento_paa é None (falha antes do iniciar)."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_RETIFICACAO_SERVICE_PATH):

        mock_service_class.return_value.preparar_documento_para_task.side_effect = Exception("Falha")
        mock_service_class.return_value.documento_paa = None

        gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    mock_service_class.return_value.marcar_erro.assert_not_called()


def test_gerar_previa_retificacao_async_retificacao_service_recebe_usuario_objeto(paa, usuario_task):
    """Testa que RetificacaoPaaService recebe o objeto User, não a string username."""
    with patch(_SERVICE_PATH), \
         patch(_GERAR_PDF_PATH), \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {
            'prioridades': {'uuid-1': {'acao': 'modificado'}}
        }

        gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username]
        )

    mock_retificacao_class.assert_called_once_with(paa=paa, usuario=usuario_task)


def test_gerar_previa_retificacao_async_falha_quando_usuario_nao_encontrado(paa):
    """Testa que a task falha quando o username informado não existe no banco."""
    result = gerar_previa_documento_paa_retificacao_async.apply(
        args=[str(paa.uuid), 'usuario_inexistente'],
        retries=MAX_RETRIES
    )

    assert result.failed()


def test_gerar_previa_retificacao_async_gerar_pdf_nao_chamado_sem_alteracoes(paa, usuario_task):
    """Testa que gerar_arquivo_documento_paa_pdf NÃO é chamado quando não há alterações."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH) as mock_gerar_pdf, \
         patch(_RETIFICACAO_SERVICE_PATH) as mock_retificacao_class:

        mock_retificacao_class.return_value.identificar_alteracoes.return_value = {}
        mock_service_class.return_value.documento_paa = MagicMock()

        gerar_previa_documento_paa_retificacao_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    mock_gerar_pdf.assert_not_called()


def test_gerar_previa_retificacao_async_marcar_erro_nao_chamado_quando_paa_nao_encontrado():
    """Testa que marcar_erro() não é chamado quando o Paa não existe.

    A falha ocorre antes da instanciação do service, fora do bloco try/except.
    """
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    with patch(_SERVICE_PATH) as mock_service_class:
        gerar_previa_documento_paa_retificacao_async.apply(
            args=[uuid_invalido, 'qualquer_usuario'],
            retries=MAX_RETRIES
        )

    mock_service_class.return_value.marcar_erro.assert_not_called()
