import pytest
from unittest.mock import patch, ANY
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.paa.tasks.gerar_documento_paa import gerar_documento_paa_async, MAX_RETRIES

pytestmark = pytest.mark.django_db

_SERVICE_PATH = 'sme_ptrf_apps.paa.tasks.gerar_documento_paa.DocumentoPaaService'
_GERAR_PDF_PATH = 'sme_ptrf_apps.paa.tasks.gerar_documento_paa.gerar_arquivo_documento_paa_pdf'


def test_gerar_documento_paa_async_sucesso(paa, usuario_task):
    """Testa que a task completa com sucesso chamando os métodos corretos do service."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH):

        result = gerar_documento_paa_async.apply(args=[str(paa.uuid), usuario_task.username])

    assert result.successful()
    mock_service_class.return_value.iniciar.assert_called_once()
    mock_service_class.return_value.marcar_concluido.assert_called_once()
    mock_service_class.return_value.marcar_erro.assert_not_called()


def test_gerar_documento_paa_async_service_criado_com_previa_false(paa, usuario_task):
    """Testa que DocumentoPaaService é instanciado com previa=False."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH):

        gerar_documento_paa_async.apply(args=[str(paa.uuid), usuario_task.username])

    mock_service_class.assert_called_once_with(
        paa=paa, usuario=usuario_task.username, previa=False, logger=ANY
    )


def test_gerar_documento_paa_async_gerar_pdf_chamado_com_previa_false(paa, usuario_task):
    """Testa que gerar_arquivo_documento_paa_pdf é chamado com previa=False."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH) as mock_gerar_pdf:

        gerar_documento_paa_async.apply(args=[str(paa.uuid), usuario_task.username])

    mock_service = mock_service_class.return_value
    mock_gerar_pdf.assert_called_once_with(paa, mock_service.documento_paa, usuario_task, previa=False)


def test_gerar_documento_paa_async_falha_gera_pdf_chama_marcar_erro(paa, usuario_task):
    """Testa que service.marcar_erro() é chamado quando a geração do PDF falha."""
    with patch(_SERVICE_PATH) as mock_service_class, \
         patch(_GERAR_PDF_PATH, side_effect=Exception("Erro ao gerar PDF")):

        result = gerar_documento_paa_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    assert result.failed()
    mock_service_class.return_value.marcar_erro.assert_called_once()


def test_gerar_documento_paa_async_falha_max_retries_excedido(paa, usuario_task):
    """Testa que MaxRetriesExceededError é levantado quando as tentativas são esgotadas."""
    with patch(_SERVICE_PATH), \
         patch(_GERAR_PDF_PATH, side_effect=Exception("Erro ao gerar PDF")):

        result = gerar_documento_paa_async.apply(
            args=[str(paa.uuid), usuario_task.username],
            retries=MAX_RETRIES
        )

    assert result.failed()
    assert isinstance(result.result, MaxRetriesExceededError)


def test_gerar_documento_paa_async_falha_quando_paa_nao_encontrado():
    """Testa que a task falha quando Paa com o UUID informado não existe."""
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    result = gerar_documento_paa_async.apply(
        args=[uuid_invalido, 'qualquer_usuario'],
        retries=MAX_RETRIES
    )

    assert result.failed()


def test_gerar_documento_paa_async_marcar_erro_nao_chamado_quando_paa_nao_encontrado():
    """Testa que marcar_erro() não é chamado quando o Paa não existe.

    A falha ocorre antes da instanciação do service, fora do bloco try/except.
    """
    uuid_invalido = '00000000-0000-0000-0000-000000000000'

    with patch(_SERVICE_PATH) as mock_service_class:
        gerar_documento_paa_async.apply(
            args=[uuid_invalido, 'qualquer_usuario'],
            retries=MAX_RETRIES
        )

    mock_service_class.return_value.marcar_erro.assert_not_called()
