import pytest
import logging
from unittest.mock import MagicMock, patch, call

from sme_ptrf_apps.paa.services.documento_paa_service import DocumentoPaaService
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
from sme_ptrf_apps.paa.models import AtaPaa

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
        paa.documentopaa_set.filter.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=2)

        service = make_service(paa=paa)
        service.apagar_documento_anteriores()

        paa.documentopaa_set.filter.assert_called_once_with(retificacao=False, versao=DocumentoPaa.VersaoChoices.PREVIA)
        mock_queryset.delete.assert_called_once()

    def test_loga_quantidade_de_documentos_encontrados(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.filter.return_value = mock_queryset
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
        paa.documentopaa_set.filter.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=0)

        service = make_service(paa=paa)
        service.apagar_documento_anteriores()

        mock_queryset.delete.assert_called_once()

    def test_filtra_apenas_documentos_nao_retificacao_por_padrao(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.filter.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=1)

        service = make_service(paa=paa)
        service.apagar_documento_anteriores()

        paa.documentopaa_set.filter.assert_called_once_with(retificacao=False, versao=DocumentoPaa.VersaoChoices.PREVIA)

    def test_filtra_apenas_documentos_retificacao_quando_retificacao_true(self):
        paa = MagicMock()
        mock_queryset = MagicMock()
        paa.documentopaa_set.filter.return_value = mock_queryset
        mock_queryset.__len__ = MagicMock(return_value=1)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=MagicMock(), retificacao=True)
        service.apagar_documento_anteriores()

        paa.documentopaa_set.filter.assert_called_once_with(retificacao=True, versao=DocumentoPaa.VersaoChoices.PREVIA)


class TestCriarNovoDocumento:
    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_chama_get_or_create_com_paa_versao_e_retificacao(self, mock_documento_paa_class):
        paa = MagicMock()
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = make_service(paa=paa, previa=True)
        service.criar_novo_documento()

        mock_documento_paa_class.objects.get_or_create.assert_called_once_with(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            retificacao=False,
            versao_documento=1,
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
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=False,
            versao_documento=1,
        )

    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_retificacao_final_usa_proxima_versao_documento(self, mock_documento_paa_class):
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = DocumentoPaaService(paa=MagicMock(), usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        service._proxima_versao_documento = 3

        service.criar_novo_documento()

        mock_documento_paa_class.objects.get_or_create.assert_called_once_with(
            paa=service.paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=True,
            versao_documento=3,
        )

    @patch('sme_ptrf_apps.paa.services.documento_paa_service.DocumentoPaa')
    def test_retificacao_previa_usa_versao_documento_1(self, mock_documento_paa_class):
        mock_doc = MagicMock()
        mock_documento_paa_class.objects.get_or_create.return_value = (mock_doc, True)
        mock_documento_paa_class.VersaoChoices = DocumentoPaa.VersaoChoices

        service = DocumentoPaaService(paa=MagicMock(), usuario=MagicMock(), previa=True,
                                      logger=MagicMock(), retificacao=True)

        service.criar_novo_documento()

        mock_documento_paa_class.objects.get_or_create.assert_called_once_with(
            paa=service.paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            retificacao=True,
            versao_documento=1,
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
        service.registrar_historico_acoes = MagicMock()

        service.marcar_concluido()

        mock_doc.arquivo_concluido.assert_called_once()

    def test_loga_concluido(self):
        mock_logger = MagicMock()
        service = make_service(mock_logger=mock_logger)
        service.documento_paa = MagicMock()
        service.registrar_historico_acoes = MagicMock()
        mock_logger.reset_mock()

        service.marcar_concluido()

        mock_logger.info.assert_called_once_with('Documento PAA concluído')


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


class TestCalcularProximaVersaoRetificacao:
    def test_retorna_1_quando_nenhum_documento_retificacao_final_existe(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        versao = service._calcular_proxima_versao_retificacao()
        assert versao == 1

    def test_retorna_versao_incrementada_quando_existem_documentos(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=True,
                   versao=DocumentoPaa.VersaoChoices.FINAL, versao_documento=2)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        versao = service._calcular_proxima_versao_retificacao()
        assert versao == 3

    def test_considera_apenas_documentos_retificacao_final(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=True,
                   versao=DocumentoPaa.VersaoChoices.PREVIA, versao_documento=5)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        versao = service._calcular_proxima_versao_retificacao()
        assert versao == 1


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

    def test_iniciar_calcula_proxima_versao_quando_retificacao_true(self):
        service = DocumentoPaaService(paa=MagicMock(), usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        service._calcular_proxima_versao_retificacao = MagicMock(return_value=2)
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        service.iniciar()

        service._calcular_proxima_versao_retificacao.assert_called_once()
        assert service._proxima_versao_documento == 2

    def test_iniciar_nao_calcula_versao_quando_retificacao_false(self):
        service = make_service(previa=False)
        service._calcular_proxima_versao_retificacao = MagicMock(return_value=2)
        service.apagar_documento_anteriores = MagicMock()
        service.criar_novo_documento = MagicMock()
        service.marcar_em_processamento = MagicMock()

        service.iniciar()

        service._calcular_proxima_versao_retificacao.assert_not_called()


class TestPrepararDocumentoParaTask:
    def test_reutiliza_previa_em_processamento_sem_chamar_iniciar(self, paa):
        from model_bakery import baker

        documento_previa = baker.make(
            DocumentoPaa,
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO,
        )
        service = make_service(paa=paa, previa=True)
        service.iniciar = MagicMock()

        service.preparar_documento_para_task()

        service.iniciar.assert_not_called()
        assert service.documento_paa == documento_previa

    def test_chama_iniciar_quando_previa_nao_esta_em_processamento(self, paa):
        service = make_service(paa=paa, previa=True)
        service.iniciar = MagicMock()

        service.preparar_documento_para_task()

        service.iniciar.assert_called_once()

    def test_chama_iniciar_para_documento_final_nao_retificacao(self, paa):
        service = make_service(paa=paa, previa=False)
        service.iniciar = MagicMock()

        service.preparar_documento_para_task()

        service.iniciar.assert_called_once()

    def test_reutiliza_final_retificacao_em_processamento_sem_chamar_iniciar(self, paa):
        from model_bakery import baker

        documento_retificacao = baker.make(
            DocumentoPaa,
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=True,
            versao_documento=1,
            status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO,
        )
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        service.iniciar = MagicMock()

        service.preparar_documento_para_task()

        service.iniciar.assert_not_called()
        assert service.documento_paa == documento_retificacao

    def test_chama_iniciar_quando_retificacao_final_nao_esta_em_processamento(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=MagicMock(), retificacao=True)
        service.iniciar = MagicMock()

        service.preparar_documento_para_task()

        service.iniciar.assert_called_once()


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
        baker.make(DocumentoPaa, paa=paa, versao=DocumentoPaa.VersaoChoices.PREVIA)
        baker.make(DocumentoPaa, paa=paa, versao=DocumentoPaa.VersaoChoices.PREVIA)

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
        baker.make(DocumentoPaa, paa=paa, versao=DocumentoPaa.VersaoChoices.PREVIA)
        baker.make(DocumentoPaa, paa=paa, versao=DocumentoPaa.VersaoChoices.PREVIA)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.iniciar()

        assert paa.documentopaa_set.count() == 1

    def test_marcar_concluido_atualiza_status_no_banco(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        service.marcar_concluido()

        service.documento_paa.refresh_from_db()
        assert service.documento_paa.status_geracao == DocumentoPaa.StatusChoices.CONCLUIDO

    def test_marcar_concluido_final_cria_ata_apresentacao(self, paa):
        assert not AtaPaa.objects.filter(paa=paa, tipo_ata=AtaPaa.ATA_APRESENTACAO).exists()

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False, logger=logger)
        service.criar_novo_documento()
        service.registrar_historico_acoes = MagicMock()
        service.marcar_concluido()

        ata = AtaPaa.objects.get(paa=paa, tipo_ata=AtaPaa.ATA_APRESENTACAO)
        assert ata.pk is not None

    def test_marcar_concluido_previa_nao_cria_ata(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        service.registrar_historico_acoes = MagicMock()
        service.marcar_concluido()

        assert not AtaPaa.objects.filter(paa=paa).exists()

    def test_marcar_concluido_documento_retificacao_nao_cria_ata(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False, logger=logger, retificacao=True)
        service.criar_novo_documento()
        service.registrar_historico_acoes = MagicMock()
        service.marcar_concluido()

        assert not AtaPaa.objects.filter(paa=paa).exists()

    def test_marcar_erro_atualiza_status_no_banco(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True, logger=logger)
        service.criar_novo_documento()
        service.marcar_erro()

        service.documento_paa.refresh_from_db()
        assert service.documento_paa.status_geracao == DocumentoPaa.StatusChoices.ERRO_PROCESSAMENTO


@pytest.mark.django_db
class TestDocumentoPaaServiceRetificacaoIntegracao:
    def test_apagar_documento_anteriores_preserva_documentos_nao_retificacao(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=False)
        baker.make(DocumentoPaa, paa=paa, retificacao=True, versao=DocumentoPaa.VersaoChoices.PREVIA)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.apagar_documento_anteriores()

        assert paa.documentopaa_set.filter(retificacao=False).count() == 1
        assert paa.documentopaa_set.filter(retificacao=True).count() == 0

    def test_apagar_documento_anteriores_preserva_retificacao_quando_nao_retificacao(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=False, versao=DocumentoPaa.VersaoChoices.PREVIA)
        baker.make(DocumentoPaa, paa=paa, retificacao=True)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=False)
        service.apagar_documento_anteriores()

        assert paa.documentopaa_set.filter(retificacao=False).count() == 0
        assert paa.documentopaa_set.filter(retificacao=True).count() == 1

    def test_criar_novo_documento_retificacao_cria_com_flag_true(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.criar_novo_documento()

        assert service.documento_paa.retificacao is True

    def test_iniciar_retificacao_cria_documento_em_processamento_com_flag_true(self, paa):
        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.iniciar()

        doc = paa.documentopaa_set.filter(retificacao=True).first()
        assert doc is not None
        assert doc.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO

    def test_iniciar_retificacao_nao_apaga_documento_final_original(self, paa):
        from model_bakery import baker
        doc_original = baker.make(DocumentoPaa, paa=paa, retificacao=False,
                                  versao=DocumentoPaa.VersaoChoices.FINAL)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.iniciar()

        assert DocumentoPaa.objects.filter(pk=doc_original.pk).exists()

    def test_versao_documento_final_retificacao_incrementa(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=True,
                   versao=DocumentoPaa.VersaoChoices.FINAL, versao_documento=2)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=logger, retificacao=True)
        service.iniciar()

        novo = paa.documentopaa_set.filter(retificacao=True, versao=DocumentoPaa.VersaoChoices.FINAL).first()
        assert novo.versao_documento == 3

    def test_preparar_documento_para_task_reutiliza_previa_retificacao_em_processamento(self, paa):
        from model_bakery import baker
        doc = baker.make(DocumentoPaa, paa=paa, retificacao=True,
                         versao=DocumentoPaa.VersaoChoices.PREVIA,
                         status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.iniciar = MagicMock()
        service.preparar_documento_para_task()

        service.iniciar.assert_not_called()
        assert service.documento_paa == doc

    def test_preparar_documento_para_task_nao_reutiliza_previa_nao_retificacao(self, paa):
        from model_bakery import baker
        baker.make(DocumentoPaa, paa=paa, retificacao=False,
                   versao=DocumentoPaa.VersaoChoices.PREVIA,
                   status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=True,
                                      logger=logger, retificacao=True)
        service.iniciar = MagicMock()
        service.preparar_documento_para_task()

        service.iniciar.assert_called_once()

    def test_preparar_documento_para_task_reutiliza_final_retificacao_em_processamento(self, paa):
        from model_bakery import baker
        doc = baker.make(DocumentoPaa, paa=paa, retificacao=True,
                         versao=DocumentoPaa.VersaoChoices.FINAL,
                         versao_documento=1,
                         status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO)

        service = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                      logger=logger, retificacao=True)
        service.iniciar = MagicMock()
        service.preparar_documento_para_task()

        service.iniciar.assert_not_called()
        assert service.documento_paa == doc

    def test_primeira_retificacao_gera_versao_documento_1(self, paa):
        # Simula o fluxo completo: viewset chama iniciar(), task chama preparar_documento_para_task()
        service_viewset = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                              logger=logger, retificacao=True)
        service_viewset.iniciar()

        service_task = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                           logger=logger, retificacao=True)
        service_task.preparar_documento_para_task()

        doc = paa.documentopaa_set.filter(
            retificacao=True, versao=DocumentoPaa.VersaoChoices.FINAL
        ).first()
        assert doc is not None
        assert doc.versao_documento == 1

    def test_segunda_retificacao_gera_versao_documento_2(self, paa):
        # Conclui a 1ª retificação
        service_1 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                        logger=logger, retificacao=True)
        service_1.iniciar()
        service_1.documento_paa.arquivo_concluido()

        # Simula 2ª retificação (viewset + task)
        service_viewset_2 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                                logger=logger, retificacao=True)
        service_viewset_2.iniciar()

        service_task_2 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                             logger=logger, retificacao=True)
        service_task_2.preparar_documento_para_task()

        doc = paa.documentopaa_set.filter(
            retificacao=True, versao=DocumentoPaa.VersaoChoices.FINAL
        ).first()
        assert doc.versao_documento == 2

    def test_terceira_retificacao_gera_versao_documento_3(self, paa):
        # 1ª retificação concluída
        s1 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                 logger=logger, retificacao=True)
        s1.iniciar()
        s1.documento_paa.arquivo_concluido()

        # 2ª retificação concluída
        s2 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                 logger=logger, retificacao=True)
        s2.iniciar()
        s2.documento_paa.arquivo_concluido()

        # 3ª retificação — viewset cria, task reutiliza
        service_viewset_3 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                                logger=logger, retificacao=True)
        service_viewset_3.iniciar()

        service_task_3 = DocumentoPaaService(paa=paa, usuario=MagicMock(), previa=False,
                                             logger=logger, retificacao=True)
        service_task_3.preparar_documento_para_task()

        doc = paa.documentopaa_set.filter(
            retificacao=True, versao=DocumentoPaa.VersaoChoices.FINAL
        ).first()
        assert doc.versao_documento == 3
