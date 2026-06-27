import pytest
from datetime import date
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import (
    ReplicaPaa,
    DocumentoPaa,
    AtaPaa,
    LogReplicaPaa,
)
from sme_ptrf_apps.paa.services.cancela_retificacao_paa_service import (
    CancelaRetificacaoPaaService,
    ValidacaoCancelaRetificacao,
)

pytestmark = pytest.mark.django_db


def _service(paa, username='usuario_teste'):
    user = type('User', (), {'username': username})()

    return CancelaRetificacaoPaaService(
        paa=paa,
        usuario=user,
    )


class TestValidacoesCancelamento:

    def test_levanta_erro_quando_flag_desabilitada(
        self,
        paa_retificacao,
    ):

        with pytest.raises(
            ValidacaoCancelaRetificacao
        ):
            _service(
                paa_retificacao
            ).valida_pode_cancelar_retificacao()

    def test_levanta_erro_quando_paa_nao_esta_em_retificacao(
        self,
        paa_factory,
        flag_paa_retificacao,
    ):

        paa = paa_factory(
            status=PaaStatusEnum.GERADO.name
        )

        with pytest.raises(
            ValidacaoCancelaRetificacao
        ):
            _service(
                paa
            ).valida_pode_cancelar_retificacao()

    def test_levanta_erro_quando_nao_existe_replica(
        self,
        paa_factory,
        flag_paa_retificacao,
        documento_paa_factory,
    ):

        paa = paa_factory(
            status=PaaStatusEnum.EM_RETIFICACAO.name
        )

        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=True,
        )

        with pytest.raises(
            ValidacaoCancelaRetificacao
        ):
            _service(
                paa
            ).valida_pode_cancelar_retificacao()

    def test_levanta_erro_quando_documento_final_foi_alterado(
        self,
        paa_retificacao,
        replica_paa,
        flag_paa_retificacao,
        documento_paa_factory,
    ):

        documento_paa_factory.create(
            paa=paa_retificacao,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            retificacao=True,
        )

        replica_paa.historico[
            'documento_retificado'
        ] = {
            'uuid': 'uuid-diferente'
        }

        replica_paa.save()

        with pytest.raises(
            ValidacaoCancelaRetificacao
        ):
            _service(
                paa_retificacao
            ).valida_pode_cancelar_retificacao()


class TestRollbackCamposSimples:

    def test_rollback_texto_introducao(
        self,
        paa_retificacao,
        replica_paa,
    ):

        paa_retificacao.texto_introducao = (
            'Texto alterado'
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        paa_retificacao.refresh_from_db()

        assert (
            paa_retificacao.texto_introducao ==
            replica_paa.historico[
                'texto_introducao'
            ]
        )

    def test_rollback_texto_conclusao(
        self,
        paa_retificacao,
        replica_paa,
    ):

        paa_retificacao.texto_conclusao = (
            'Conclusao alterada'
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        paa_retificacao.refresh_from_db()

        assert (
            paa_retificacao.texto_conclusao ==
            replica_paa.historico[
                'texto_conclusao'
            ]
        )


class TestRollbackOutrosRelacionamentos:

    def test_rollback_remove_objetivo_adicionado(
        self,
        paa_retificacao,
        replica_paa,
        objetivo_paa_factory,
    ):

        objetivo = (
            objetivo_paa_factory.create(
                paa=paa_retificacao,
                nome='Novo objetivo'
            )
        )

        service = _service(
            paa_retificacao
        )

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert not (
            objetivo.__class__.objects.filter(
                pk=objetivo.pk
            ).exists()
        )

    def test_rollback_recria_objetivo_removido(
        self,
        paa_retificacao,
        replica_paa_factory,
        prioridade_no_paa,
        objetivo_no_paa,
    ):

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        nome_objetivo = (
            objetivo_no_paa.nome
        )

        objetivo_no_paa.delete()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert (
            paa_retificacao
            .objetivopaa_set
            .filter(nome=nome_objetivo)
            .exists()
        )

    def test_rollback_restaura_prioridade_modificada(
        self,
        paa_retificacao,
        replica_paa_factory,
        prioridade_no_paa,
    ):

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        valor_original = (
            prioridade_no_paa.valor_total
        )

        prioridade_no_paa.valor_total = 9999
        prioridade_no_paa.save()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        prioridade_no_paa.refresh_from_db()

        assert str(prioridade_no_paa.valor_total) == valor_original

    def test_rollback_restaura_receita_ptrf_modificada(
        self,
        paa_retificacao,
        replica_paa_factory,
        receita_ptrf_no_paa,
    ):

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        valor_original = (
            str(
                receita_ptrf_no_paa
                .previsao_valor_custeio
            )
        )

        receita_ptrf_no_paa.previsao_valor_custeio = 9999
        receita_ptrf_no_paa.save()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        receita_ptrf_no_paa.refresh_from_db()

        assert (
            str(
                receita_ptrf_no_paa
                .previsao_valor_custeio
            ) == valor_original
        )

    def test_rollback_remove_receita_pdde_adicionada(
        self,
        paa_retificacao,
        replica_paa_factory,
        receita_prevista_pdde_factory,
        acao_pdde,
    ):

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        receita = (
            receita_prevista_pdde_factory.create(
                paa=paa_retificacao,
                acao_pdde=acao_pdde,
                previsao_valor_custeio='800.00',
                previsao_valor_capital='400.00',
                previsao_valor_livre='0.00',
                saldo_custeio='0.00',
                saldo_capital='0.00',
                saldo_livre='0.00',
            )
        )

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert not (
            receita.__class__.objects.filter(
                pk=receita.pk
            ).exists()
        )

    def test_rollback_recria_atividade_estatutaria_removida(
        self,
        paa_retificacao,
        replica_paa_factory,
        atividade_estatutaria_factory,
        atividade_estatutaria_paa_factory,
    ):

        atividade = atividade_estatutaria_factory.create(
            nome="Atividade 1",
            paa=paa_retificacao
        )

        atividade_estatutaria_paa = atividade_estatutaria_paa_factory(
            paa=paa_retificacao,
            atividade_estatutaria=atividade,
            data=date(2023, 6, 5)
        )

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        uuid_original = str(
            atividade_estatutaria_paa
            .atividade_estatutaria
            .uuid
        )

        atividade_estatutaria_paa.delete()
        atividade.delete()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert (
            paa_retificacao
            .atividadeestatutariapaa_set
            .filter(
                atividade_estatutaria__uuid=uuid_original
            )
            .exists()
        )

    def test_rollback_restaura_atividade_estatutaria_modificada(
        self,
        paa_retificacao,
        replica_paa_factory,
        atividade_estatutaria_factory,
        atividade_estatutaria_paa_factory,
    ):

        atividade = atividade_estatutaria_factory.create(
            nome="Atividade 1",
            paa=paa_retificacao
        )

        atividade_estatutaria_paa = atividade_estatutaria_paa_factory(
            paa=paa_retificacao,
            atividade_estatutaria=atividade,
            data=date(2023, 6, 5)
        )
        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        nome_original = (
            atividade_estatutaria_paa
            .atividade_estatutaria
            .nome
        )

        atividade_estatutaria_paa.atividade_estatutaria.nome = (
            'Nome alterado'
        )

        atividade_estatutaria_paa.atividade_estatutaria.save()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        atividade_estatutaria_paa.refresh_from_db()

        assert (
            atividade_estatutaria_paa
            .atividade_estatutaria
            .nome == nome_original
        )

    def test_rollback_recria_recurso_proprio_removido(
        self,
        paa_retificacao,
        replica_paa_factory,
        recurso_proprio_paa_factory,
        fonte_recurso_paa_factory,
    ):

        fonte = fonte_recurso_paa_factory.create()

        recurso_proprio = recurso_proprio_paa_factory.create(
            paa=paa_retificacao,
            associacao=paa_retificacao.associacao,
            fonte_recurso=fonte,
            valor='1000.00',
            descricao='Recurso próprio de integração',
        )

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        uuid_original = (
            recurso_proprio.uuid
        )

        recurso_proprio.delete()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert (
            paa_retificacao
            .recursopropriopaa_set
            .filter(uuid=uuid_original)
            .exists()
        )

    def test_rollback_restaura_recurso_proprio_modificado(
        self,
        paa_retificacao,
        replica_paa_factory,
        recurso_proprio_paa_factory,
        fonte_recurso_paa_factory,
    ):

        fonte = fonte_recurso_paa_factory.create()

        recurso_proprio = recurso_proprio_paa_factory.create(
            paa=paa_retificacao,
            associacao=paa_retificacao.associacao,
            fonte_recurso=fonte,
            valor='1000.00',
            descricao='Recurso próprio de integração',
        )

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        descricao_original = (
            recurso_proprio.descricao
        )

        recurso_proprio.descricao = (
            'Descricao alterada'
        )

        recurso_proprio.save()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        recurso_proprio.refresh_from_db()

        assert (
            recurso_proprio.descricao ==
            descricao_original
        )

    def test_rollback_remove_prioridade_adicionada(
        self,
        paa_retificacao,
        replica_paa_factory,
        prioridade_paa_factory,
    ):
        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        prioridade = (
            prioridade_paa_factory.create(
                paa=paa_retificacao,
                valor_total=5000
            )
        )

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert not (
            prioridade.__class__.objects.filter(
                pk=prioridade.pk
            ).exists()
        )

    def test_rollback_recria_prioridade_removida(
        self,
        paa_retificacao,
        replica_paa_factory,
        prioridade_paa_factory,
    ):

        service = _service(
            paa_retificacao
        )

        prioridade = (
            prioridade_paa_factory.create(
                paa=paa_retificacao,
                valor_total=5000
            )
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        uuid_original = str(
            prioridade.uuid
        )

        valor_total_original = (
            prioridade.valor_total
        )

        prioridade.delete()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        assert (
            paa_retificacao
            .prioridadepaa_set
            .filter(
                uuid=uuid_original,
                valor_total=valor_total_original,
            )
            .exists()
        )

    def test_rollback_restaura_prioridade_modificada_2(
        self,
        paa_retificacao,
        replica_paa_factory,
        prioridade_paa_factory,
    ):

        prioridade = (
            prioridade_paa_factory.create(
                paa=paa_retificacao,
                valor_total=5000,
                prioridade=True
            )
        )

        service = _service(
            paa_retificacao
        )

        novo_historico = (
            service.retificacao_service
            .gerar_snapshot()
        )

        replica_paa_factory(
            paa=paa_retificacao,
            historico=novo_historico
        )

        prioridade_original = bool(
            prioridade.prioridade
        )

        prioridade.valor_total = False
        prioridade.save()

        alteracoes = (
            service.retificacao_service
            .identificar_alteracoes()
        )

        service.executar_rollbacks(
            alteracoes
        )

        prioridade.refresh_from_db()

        assert prioridade.prioridade == prioridade_original


class TestLimpezaPosRollback:

    def test_remove_documentos_previos_retificacao(
        self,
        paa_retificacao,
        documento_paa_factory,
    ):

        documento = (
            documento_paa_factory.create(
                paa=paa_retificacao,
                versao=DocumentoPaa.VersaoChoices.PREVIA,
                retificacao=True,
            )
        )

        service = _service(
            paa_retificacao
        )

        service._remover_documentos_previos()

        assert not (
            DocumentoPaa.objects.filter(
                pk=documento.pk
            ).exists()
        )

    def test_remove_atas_previas_retificacao(
        self,
        paa_retificacao,
        ata_paa_factory,
    ):

        ata = ata_paa_factory.create(
            paa=paa_retificacao,
            tipo_ata=AtaPaa.ATA_RETIFICACAO,
            previa=True,
        )

        service = _service(
            paa_retificacao
        )

        service._remover_atas_previas()

        assert not (
            AtaPaa.objects.filter(
                pk=ata.pk
            ).exists()
        )


class TestCancelamentoRetificacao:

    def test_executa_cancelamento_com_sucesso(
        self,
        paa_retificacao,
        replica_paa,
        flag_paa_retificacao,
    ):

        paa_retificacao.status = (
            PaaStatusEnum.EM_RETIFICACAO.name
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        service.iniciar_cancelamento_retificacao()

        paa_retificacao.refresh_from_db()

        assert (
            paa_retificacao.status ==
            PaaStatusEnum.GERADO.name
        )

        assert not (
            ReplicaPaa.objects.filter(
                paa=paa_retificacao
            ).exists()
        )

        assert (
            LogReplicaPaa.objects.filter(
                paa=paa_retificacao,
                origem=LogReplicaPaa.CANCELAMENTO,
            ).exists()
        )

    def test_cria_log_replica_no_cancelamento(
        self,
        paa_retificacao,
        replica_paa,
        flag_paa_retificacao,
    ):

        paa_retificacao.status = (
            PaaStatusEnum.EM_RETIFICACAO.name
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        service.iniciar_cancelamento_retificacao()

        assert (
            LogReplicaPaa.objects.filter(
                paa=paa_retificacao,
                origem=LogReplicaPaa.CANCELAMENTO,
            ).count() == 1
        )

    def test_remove_replica_apos_cancelamento(
        self,
        paa_retificacao,
        replica_paa,
        flag_paa_retificacao,
    ):

        paa_retificacao.status = (
            PaaStatusEnum.EM_RETIFICACAO.name
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        service.iniciar_cancelamento_retificacao()

        assert not (
            ReplicaPaa.objects.filter(
                paa=paa_retificacao
            ).exists()
        )

    def test_retorna_status_para_gerado(
        self,
        paa_retificacao,
        replica_paa,
        flag_paa_retificacao,
    ):

        paa_retificacao.status = (
            PaaStatusEnum.EM_RETIFICACAO.name
        )

        paa_retificacao.save()

        service = _service(
            paa_retificacao
        )

        service.iniciar_cancelamento_retificacao()

        paa_retificacao.refresh_from_db()

        assert (
            paa_retificacao.status ==
            PaaStatusEnum.GERADO.name
        )
