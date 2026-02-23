import pytest
import logging
from unittest.mock import MagicMock, patch, call

from sme_ptrf_apps.paa.services.documento_paa_service import DocumentoPaaService
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa

logger = logging.getLogger(__name__)


def make_service(paa=None, usuario=None, previa=True, mock_logger=None):
    paa = paa or MagicMock()
    usuario = usuario or MagicMock()
    mock_logger = mock_logger or MagicMock()
    return DocumentoPaaService(paa=paa, usuario=usuario, previa=previa, logger=mock_logger)


class TestDocumentoPaaServiceInit:
    def test_versao_previa_quando_previa_true(self):
        service = make_service(previa=True)
        assert service.versao == DocumentoPaa.VersaoChoices.PREVIA

    def test_versao_final_quando_previa_false(self):
        service = make_service(previa=False)
        assert service.versao == DocumentoPaa.VersaoChoices.FINAL

    def test_documento_paa_inicia_como_none(self):
        service = make_service()
        assert service.documento_paa is None

    def test_atributos_recebidos_salvos(self):
        paa = MagicMock()
        usuario = MagicMock()
        mock_logger = MagicMock()

        service = DocumentoPaaService(paa=paa, usuario=usuario, previa=True, logger=mock_logger)

        assert service.paa is paa
        assert service.usuario is usuario
        assert service.previa is True
        assert service.logger is mock_logger

    def test_logger_info_chamado_na_inicializacao(self):
        mock_logger = MagicMock()
        make_service(mock_logger=mock_logger)
        mock_logger.info.assert_called_once_with('Inicializando DocumentoPaaService...')


class TestApagarDocumentosAnteriores:
    def test_deleta_documentos_anteriores(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.all.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=2)

        service = make_service(paa=paa)
        service.apagar_documento_anteriores()

        paa.documentopaa_set.all.assert_called_once()
        mock_queryset.delete.assert_called_once()

    def test_loga_quantidade_de_documentos_encontrados(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.all.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=3)

        mock_logger = MagicMock()
        service = make_service(paa=paa, mock_logger=mock_logger)
        mock_logger.reset_mock()

        service.apagar_documento_anteriores()

        calls = [c[0][0] for c in mock_logger.info.call_args_list]
        assert any('Documentos anteriores encontrados' in msg for msg in calls)
        assert any('Documentos anteriores apagados com sucesso' in msg for msg in calls)

    def test_delete_chamado_mesmo_sem_documentos(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.all.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=0)

        service = make_service(paa=paa)
        service.apagar_documento_anteriores()

        mock_queryset.delete.assert_called_once()


class TestCriarNovoDocumento:
    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_chama_get_or_create_com_paa_e_versao(self, mock_documento_paa_class):
        paa = MagicMock()
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = make_service(paa=paa, previa=True)
        service.criar_novo_documento()

        mock_documento_paa_class.objects.get_or_create.assert_called_once_with(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA
        )

    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_atribui_documento_criado_a_self(self, mock_documento_paa_class):
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = make_service(previa=False)
        service.criar_novo_documento()

        assert service.documento_paa is mock_doc

    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_loga_criacao_do_documento(self, mock_documento_paa_class):
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        mock_logger = MagicMock()
        service = make_service(previa=True, mock_logger=mock_logger)
        mock_logger.reset_mock()

        service.criar_novo_documento()

        calls = [c[0][0] for c in mock_logger.info.call_args_list]
        assert any('criado com sucesso' in msg for msg in calls)

    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_usa_versao_final_quando_previa_false(self, mock_documento_paa_class):
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = make_service(previa=False)
        service.criar_novo_documento()

        mock_documento_paa_class.objects.get_or_create.assert_called_once_with(
            paa=service.paa,
            versao=DocumentoPaa.VersaoChoices.FINAL
        )


class TestMarcarEmProcessamento:
    def test_chama_arquivo_em_processamento(self):
        mock_doc = MagicMock()
        service = make_service()
        service.documento_paa = mock_doc

        service.marcar_em_processamento()

        mock_doc.arquivo_em_processamento.assert_called_once()

    def test_loga_em_processamento(self):
        mock_logger = MagicMock()
        service = make_service(mock_logger=mock_logger)
        service.documento_paa = MagicMock()
        mock_logger.reset_mock()

        service.marcar_em_processamento()

        mock_logger.info.assert_called_once_with('Documento PAA em processamento')


class TestMarcarConcluido:
    def test_chama_arquivo_concluido(self):
        mock_doc = MagicMock()
        service = make_service()
        service.documento_paa = mock_doc

        service.marcar_concluido()

        mock_doc.arquivo_concluido.assert_called_once()

    def test_loga_concluido(self):
        mock_logger = MagicMock()
        service = make_service(mock_logger=mock_logger)
        service.documento_paa = MagicMock()
        mock_logger.reset_mock()

        service.marcar_concluido()

        mock_logger.info.assert_called_once_with('Documento PAA concluido')


class TestMarcarErro:
    def test_chama_arquivo_em_erro_processamento(self):
        mock_doc = MagicMock()
        service = make_service()
        service.documento_paa = mock_doc

        service.marcar_erro()

        mock_doc.arquivo_em_erro_processamento.assert_called_once()

    def test_loga_erro(self):
        mock_logger = MagicMock()
        service = make_service(mock_logger=mock_logger)
        service.documento_paa = MagicMock()
        mock_logger.reset_mock()

        service.marcar_erro()

        mock_logger.info.assert_called_once_with('Documento PAA marcado com erro no processamento')


class TestIniciar:
    def test_iniciar_chama_metodos_na_ordem_correta(self):
        service = make_service()
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        manager = MagicMock()
        manager.attach_mock(service.apagar_documento_anteriores, 'apagar')
        manager.attach_mock(service.criar_novo_documento, 'criar')
        manager.attach_mock(service.marcar_em_processamento, 'marcar')

        service.iniciar()

        assert manager.mock_calls == [
            call.apagar(),
            call.criar(),
            call.marcar(),
        ]

    def test_iniciar_delega_para_apagar_documento_anteriores(self):
        service = make_service()
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        service.iniciar()

        service.apagar_documento_anteriores.assert_called_once()

    def test_iniciar_delega_para_criar_novo_documento(self):
        service = make_service()
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        service.iniciar()

        service.criar_novo_documento.assert_called_once()

    def test_iniciar_delega_para_marcar_em_processamento(self):
        service = make_service()
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        service.iniciar()

        service.marcar_em_processamento.assert_called_once()


@pytest.mark.django_db
class TestDocumentoPaaServiceIntegracao:
    def test_criar_novo_documento_persiste_no_banco(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()

        assert service.documento_paa is not None
        assert service.documento_paa.pk is not None
        assert service.documento_paa.paa == paa
        assert service.documento_paa.versao == DocumentoPaa.VersaoChoices.PREVIA

    def test_criar_novo_documento_versao_final(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False, logger=logger)
        service.criar_novo_documento()

        assert service.documento_paa.versao == DocumentoPaa.VersaoChoices.FINAL

    def test_criar_novo_documento_idempotente(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        primeiro_pk = service.documento_paa.pk

        service.criar_novo_documento()
        segundo_pk = service.documento_paa.pk

        assert primeiro_pk == segundo_pk

    def test_apagar_documento_anteriores_remove_documentos_do_banco(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa)
        baker.make(DocumentoPaa, paa=paa)

        assert paa.documentopaa_set.count() == 2

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.apagar_documento_anteriores()

        assert paa.documentopaa_set.count() == 0

    def test_iniciar_cria_documento_em_processamento(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.iniciar()

        assert service.documento_paa is not None
        assert service.documento_paa.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO

    def test_iniciar_apaga_documentos_anteriores(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa)
        baker.make(DocumentoPaa, paa=paa)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.iniciar()

        assert paa.documentopaa_set.count() == 1

    def test_marcar_concluido_atualiza_status_no_banco(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        service.marcar_concluido()

        service.documento_paa.refresh_from_db()
        assert service.documento_paa.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO

    def test_marcar_erro_atualiza_status_no_banco(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        service.marcar_erro()

        service.documento_paa.refresh_from_db()
        assert service.documento_paa.status_geracao == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO
