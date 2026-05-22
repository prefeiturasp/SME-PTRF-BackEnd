import pytest

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

        documento = documento_paa_factory.create(
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


class TestRollbackRelacionamentos:

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
        replica_paa,
        prioridade_no_paa,
        objetivo_no_paa,
    ):

        nome_objetivo = (
            objetivo_no_paa.nome
        )

        objetivo_no_paa.delete()

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

        assert (
            paa_retificacao
            .objetivopaa_set
            .filter(nome=nome_objetivo)
            .exists()
        )

    def test_rollback_restaura_prioridade_modificada(
        self,
        paa_retificacao,
        replica_paa,
        prioridade_no_paa,
    ):

        valor_original = (
            prioridade_no_paa.valor_total
        )

        prioridade_no_paa.valor_total = 9999
        prioridade_no_paa.save()

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

        prioridade_no_paa.refresh_from_db()

        assert (
            prioridade_no_paa.valor_total ==
            valor_original
        )


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