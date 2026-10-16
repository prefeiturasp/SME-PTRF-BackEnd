"""Testes de concorrência entre o request e as tasks do Consolidado DRE.

Regressão: o consolidado publicado (FINAL) voltava para PREVIA.

A task de publicação carregava o consolidado antes do commit do request (ATOMIC_REQUESTS) e,
ao final, passar_para_status_gerado fazia save() de todos os campos, sobrescrevendo a
versão FINAL pela versão PREVIA que estava na instância em memória.

As funções gerar_previa_consolidado_dre e concluir_consolidado_dre são
@transaction.atomic e só enfileiram a task via transaction.on_commit.
"""
from unittest import mock

import pytest
from django.db import connection, transaction

from ...models import ConsolidadoDRE
from ...services import consolidado_dre_service

pytestmark = pytest.mark.django_db


@pytest.fixture
def consolidado_dre_previa_gerado(consolidado_dre_teste_model_consolidado_dre):
    """Consolidado DRE na versão PREVIA, com documentos totais gerados.

    Args:
        consolidado_dre_teste_model_consolidado_dre: Consolidado DRE base da fixture do model.

    Returns:
        ConsolidadoDRE: Instância recarregada do banco após a atualização.
    """
    consolidado = consolidado_dre_teste_model_consolidado_dre
    ConsolidadoDRE.objects.filter(pk=consolidado.pk).update(
        versao=ConsolidadoDRE.VERSAO_PREVIA,
        status=ConsolidadoDRE.STATUS_GERADOS_TOTAIS,
        sequencia_de_publicacao=0,
        eh_parcial=False,
    )
    return ConsolidadoDRE.objects.get(pk=consolidado.pk)


def test_passar_para_status_gerado_com_instancia_desatualizada_nao_sobrescreve_versao_final(
    consolidado_dre_previa_gerado
):
    """Testa que uma instância desatualizada na task não sobrescreve a versão FINAL publicada.

    Simula a task carregando o consolidado como PREVIA, a publicação sendo commitada em
    seguida e a task concluindo com a instância antiga via passar_para_status_gerado.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
    """
    instancia_da_task = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)

    ConsolidadoDRE.objects.filter(pk=consolidado_dre_previa_gerado.pk).update(
        versao=ConsolidadoDRE.VERSAO_FINAL,
        status=ConsolidadoDRE.STATUS_EM_PROCESSAMENTO,
    )

    instancia_da_task.passar_para_status_gerado(parcial=False)

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.versao == ConsolidadoDRE.VERSAO_FINAL
    assert consolidado.status == ConsolidadoDRE.STATUS_GERADOS_TOTAIS


def test_passar_para_status_em_processamento_altera_apenas_status(consolidado_dre_previa_gerado):
    """Testa que passar_para_status_em_processamento grava somente o campo status.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
    """
    instancia_desatualizada = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    ConsolidadoDRE.objects.filter(pk=consolidado_dre_previa_gerado.pk).update(versao=ConsolidadoDRE.VERSAO_FINAL)

    instancia_desatualizada.passar_para_status_em_processamento()

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.status == ConsolidadoDRE.STATUS_EM_PROCESSAMENTO
    assert consolidado.versao == ConsolidadoDRE.VERSAO_FINAL


def test_atribuir_versao_altera_apenas_versao(consolidado_dre_previa_gerado):
    """Testa que atribuir_versao grava somente o campo versao.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
    """
    instancia_desatualizada = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    ConsolidadoDRE.objects.filter(pk=consolidado_dre_previa_gerado.pk).update(
        status=ConsolidadoDRE.STATUS_EM_PROCESSAMENTO
    )

    instancia_desatualizada.atribuir_versao(previa=False)

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.versao == ConsolidadoDRE.VERSAO_FINAL
    assert consolidado.status == ConsolidadoDRE.STATUS_EM_PROCESSAMENTO


def test_atribuir_se_eh_parcial_altera_apenas_eh_parcial(consolidado_dre_previa_gerado):
    """Testa que atribuir_se_eh_parcial grava somente o campo eh_parcial.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
    """
    instancia_desatualizada = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    ConsolidadoDRE.objects.filter(pk=consolidado_dre_previa_gerado.pk).update(versao=ConsolidadoDRE.VERSAO_FINAL)

    instancia_desatualizada.atribuir_se_eh_parcial(parcial=True)

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.eh_parcial is True
    assert consolidado.versao == ConsolidadoDRE.VERSAO_FINAL


def test_concluir_consolidado_dre_enfileira_task_somente_apos_commit(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
    django_capture_on_commit_callbacks,
):
    """Testa que concluir_consolidado_dre só enfileira a task de publicação após o commit.

    Captura os callbacks de on_commit sem executá-los, verifica que a task ainda não foi
    enfileirada e que o consolidado já está FINAL e em processamento, e então executa o
    callback para confirmar o enfileiramento com o uuid do consolidado.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
        django_capture_on_commit_callbacks: Captura os callbacks registrados via on_commit.
    """
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "concluir_consolidado_dre_async") as task_mock:
        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            consolidado = consolidado_dre_service.concluir_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

        task_mock.delay.assert_not_called()
        assert len(callbacks) == 1

        consolidado.refresh_from_db()
        assert consolidado.versao == ConsolidadoDRE.VERSAO_FINAL
        assert consolidado.status == ConsolidadoDRE.STATUS_EM_PROCESSAMENTO

        callbacks[0]()

        task_mock.delay.assert_called_once()
        assert task_mock.delay.call_args.kwargs["consolidado_dre_uuid"] == consolidado.uuid


def test_gerar_previa_consolidado_dre_enfileira_task_somente_apos_commit(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
    django_capture_on_commit_callbacks,
):
    """Testa que gerar_previa_consolidado_dre só enfileira a task de prévia após o commit.

    Captura os callbacks de on_commit sem executá-los, verifica que a task ainda não foi
    enfileirada e então executa o callback para confirmar o enfileiramento.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
        django_capture_on_commit_callbacks: Captura os callbacks registrados via on_commit.
    """
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "gerar_previa_consolidado_dre_async") as task_mock:
        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            consolidado_dre_service.gerar_previa_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

        task_mock.apply_async.assert_not_called()
        assert len(callbacks) == 1

        callbacks[0]()

        task_mock.apply_async.assert_called_once()


def _registrar_estado_no_enfileiramento(consolidado_pk, estado):
    """Cria um side effect que registra o estado do banco no momento do enfileiramento.

    Args:
        consolidado_pk: Chave primária do consolidado a ser inspecionado.
        estado: Dicionário preenchido com em_transacao, versao e status.

    Returns:
        Callable: Função para usar como side_effect do mock da task.
    """
    def _side_effect(*args, **kwargs):
        estado["em_transacao"] = connection.in_atomic_block
        estado["versao"], estado["status"] = ConsolidadoDRE.objects.filter(
            pk=consolidado_pk).values_list("versao", "status").get()
    return _side_effect


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("dentro_de_transacao", [True, False], ids=["atomic_requests", "autocommit"])
def test_publicacao_so_enfileira_task_com_versao_final_ja_gravada(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
    dentro_de_transacao,
):
    """Testa que a task de publicação só é enfileirada com a versão FINAL já gravada.

    Registra, no momento do enfileiramento, se há transação aberta e a versão/status do
    consolidado no banco. Garante a regra com e sem ATOMIC_REQUESTS. Se o
    transaction.on_commit for trocado por uma chamada direta, este teste falha.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
        dentro_de_transacao: Se True, envolve a chamada em transaction.atomic para simular
            ATOMIC_REQUESTS; se False, executa em autocommit.
    """
    estado = {}
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "concluir_consolidado_dre_async") as task_mock:
        task_mock.delay.side_effect = _registrar_estado_no_enfileiramento(consolidado_dre_previa_gerado.pk, estado)

        def publicar():
            consolidado_dre_service.concluir_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

        if dentro_de_transacao:
            with transaction.atomic():
                publicar()
                task_mock.delay.assert_not_called()
        else:
            publicar()

    task_mock.delay.assert_called_once()
    assert estado["em_transacao"] is False
    assert estado["versao"] == ConsolidadoDRE.VERSAO_FINAL
    assert estado["status"] == ConsolidadoDRE.STATUS_EM_PROCESSAMENTO


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("dentro_de_transacao", [True, False], ids=["atomic_requests", "autocommit"])
def test_previa_so_enfileira_task_com_versao_previa_ja_gravada(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
    dentro_de_transacao,
):
    """Testa que a task de prévia só é enfileirada com a versão PREVIA já gravada.

    Registra, no momento do enfileiramento, se há transação aberta e a versão/status do
    consolidado no banco. Garante a regra com e sem ATOMIC_REQUESTS. Se o
    transaction.on_commit for trocado por uma chamada direta, este teste falha.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
        dentro_de_transacao: Se True, envolve a chamada em transaction.atomic para simular
            ATOMIC_REQUESTS; se False, executa em autocommit.
    """
    estado = {}
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "gerar_previa_consolidado_dre_async") as task_mock:
        task_mock.apply_async.side_effect = _registrar_estado_no_enfileiramento(
            consolidado_dre_previa_gerado.pk, estado)

        def gerar_previa():
            consolidado_dre_service.gerar_previa_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

        if dentro_de_transacao:
            with transaction.atomic():
                gerar_previa()
                task_mock.apply_async.assert_not_called()
        else:
            gerar_previa()

    task_mock.apply_async.assert_called_once()
    assert estado["em_transacao"] is False
    assert estado["versao"] == ConsolidadoDRE.VERSAO_PREVIA
    assert estado["status"] == ConsolidadoDRE.STATUS_EM_PROCESSAMENTO


@pytest.mark.django_db(transaction=True)
def test_concluir_consolidado_dre_com_erro_faz_rollback_e_nao_enfileira_task(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
):
    """Testa que uma falha em concluir_consolidado_dre faz rollback e não enfileira a task.

    Força um erro na criação da ata, depois que versão e status já foram alterados, e
    verifica que o consolidado volta ao estado original. O on_commit registrado dentro do
    @transaction.atomic é descartado no rollback.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
    """
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "concluir_consolidado_dre_async") as task_mock, \
            mock.patch.object(consolidado_dre_service.AtaParecerTecnico, "criar_ou_retornar_ata_sem_consolidado_dre",
                              side_effect=Exception("falha ao criar ata")):
        with pytest.raises(Exception, match="falha ao criar ata"):
            consolidado_dre_service.concluir_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

    task_mock.delay.assert_not_called()

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.versao == ConsolidadoDRE.VERSAO_PREVIA
    assert consolidado.status == ConsolidadoDRE.STATUS_GERADOS_TOTAIS


@pytest.mark.django_db(transaction=True)
def test_gerar_previa_consolidado_dre_com_erro_faz_rollback_e_nao_enfileira_task(
    consolidado_dre_previa_gerado,
    dre_teste_model_consolidado_dre,
    periodo_teste_model_consolidado_dre,
):
    """Testa que uma falha em gerar_previa_consolidado_dre faz rollback e não enfileira a task.

    Força um erro em atribuir_se_eh_parcial, depois que o status já foi alterado, e
    verifica que o consolidado volta ao estado original. O on_commit registrado dentro do
    @transaction.atomic é descartado no rollback.

    Args:
        consolidado_dre_previa_gerado: Consolidado DRE na versão PREVIA com documentos gerados.
        dre_teste_model_consolidado_dre: DRE do consolidado.
        periodo_teste_model_consolidado_dre: Período do consolidado.
    """
    parcial = {"parcial": False, "sequencia_de_publicacao_atual": 0}

    with mock.patch.object(consolidado_dre_service, "gerar_previa_consolidado_dre_async") as task_mock, \
            mock.patch.object(ConsolidadoDRE, "atribuir_se_eh_parcial", side_effect=Exception("falha")):
        with pytest.raises(Exception, match="falha"):
            consolidado_dre_service.gerar_previa_consolidado_dre(
                dre=dre_teste_model_consolidado_dre,
                periodo=periodo_teste_model_consolidado_dre,
                parcial=parcial,
                usuario="usuario_teste",
                uuid_retificacao=None,
            )

    task_mock.apply_async.assert_not_called()

    consolidado = ConsolidadoDRE.objects.get(pk=consolidado_dre_previa_gerado.pk)
    assert consolidado.status == ConsolidadoDRE.STATUS_GERADOS_TOTAIS
