import pytest

from sme_ptrf_apps.paa.models import Paa, DocumentoPaa, AtaPaa
from sme_ptrf_apps.paa.enums import PaaStatusEnum, PaaStatusAndamentoEnum
from sme_ptrf_apps.paa.paa_querysets.paa_queryset import PaaQuerySet

pytestmark = pytest.mark.django_db


def _qs():
    """Retorna um queryset de Paa usando o PaaQuerySet."""
    return PaaQuerySet(model=Paa, using=Paa.objects.db)


class TestAnnotateStatusGeracao:
    def test_status_nao_iniciado_andamento_tambem_nao_iniciado(
        self, paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.NAO_INICIADO.name,
        )

        qs = _qs().filter(pk=paa.pk).filter_por_status_geracao(PaaStatusAndamentoEnum.NAO_INICIADO.name)
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.NAO_INICIADO.name

    def test_status_gerado_com_documento_final_concluido_e_ata_concluida(
        self, paa_factory, documento_paa_factory, ata_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.GERADO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk).paas_gerados()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.GERADO.name

    def test_status_gerado_sem_documento_final_concluido_retorna_em_elaboracao(
        self, paa_factory, ata_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.GERADO.name,
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk).paas_em_elaboracao()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.EM_ELABORACAO.name

    def test_status_gerado_sem_ata_concluida_retorna_fora_fluxo(
        self, paa_factory, documento_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.GERADO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk)
        assert qs.first().get_status_andamento() == PaaStatusAndamentoEnum.FORA_FLUXO.name

    def test_status_em_retificacao_retorna_gerado_parcialmente(
        self, paa_factory, periodo_paa_factory, associacao, documento_paa_factory, ata_paa_factory
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.EM_RETIFICACAO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk).paas_gerados_parcialmente()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name

    def test_status_em_elaboracao_com_documento_final_concluido_retorna_gerado_parcialmente(
        self, paa_factory, documento_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.EM_ELABORACAO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk).paas_gerados_parcialmente()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name

    def test_status_em_elaboracao_sem_documento_retorna_em_elaboracao(
        self, paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.EM_ELABORACAO.name,
        )

        qs = _qs().filter(pk=paa.pk).paas_em_elaboracao()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.EM_ELABORACAO.name

    def test_status_em_elaboracao_com_documento_previa_retorna_em_elaboracao(
        self, paa_factory, documento_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.EM_ELABORACAO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        qs = _qs().filter(pk=paa.pk).paas_em_elaboracao()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.EM_ELABORACAO.name

    def test_status_em_elaboracao_com_documento_final_em_processamento_retorna_em_elaboracao(
        self, paa_factory, documento_paa_factory, periodo_paa_factory, associacao
    ):
        periodo = periodo_paa_factory.create()
        paa = paa_factory.create(
            periodo_paa=periodo,
            associacao=associacao,
            status=PaaStatusEnum.EM_ELABORACAO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO,
        )

        qs = _qs().filter(pk=paa.pk).paas_em_elaboracao()
        assert qs.first().status_andamento == PaaStatusAndamentoEnum.EM_ELABORACAO.name


class TestFilterPorStatusGeracao:
    def test_filtra_somente_gerados(
        self, paa_factory, documento_paa_factory, ata_paa_factory, periodo_paa_factory, associacao_factory
    ):
        periodo = periodo_paa_factory.create()

        # PAA gerado
        assoc1 = associacao_factory.create()
        paa_gerado = paa_factory.create(
            periodo_paa=periodo, associacao=assoc1, status=PaaStatusEnum.GERADO.name
        )
        documento_paa_factory.create(
            paa=paa_gerado,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        ata_paa_factory.create(paa=paa_gerado, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)

        # PAA em elaboracao
        assoc2 = associacao_factory.create()
        paa_factory.create(
            periodo_paa=periodo, associacao=assoc2, status=PaaStatusEnum.EM_ELABORACAO.name
        )

        resultado = _qs().filter_por_status_geracao(PaaStatusAndamentoEnum.GERADO.name)
        assert resultado.count() == 1
        assert resultado.first().pk == paa_gerado.pk
        resultado_qs = _qs().paas_gerados()
        assert resultado_qs.count() == 1
        assert resultado_qs.first().pk == paa_gerado.pk

    def test_filtra_somente_gerados_parcialmente(
        self, paa_factory, documento_paa_factory, periodo_paa_factory, associacao_factory, ata_paa_factory
    ):
        periodo = periodo_paa_factory.create()

        # PAA em retificacao
        assoc1 = associacao_factory.create()
        paa_retificacao = paa_factory.create(
            periodo_paa=periodo, associacao=assoc1, status=PaaStatusEnum.EM_RETIFICACAO.name
        )
        documento_paa_factory.create(
            paa=paa_retificacao,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        ata_paa_factory.create(paa=paa_retificacao, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)

        # PAA em elaboracao com doc final
        assoc2 = associacao_factory.create()
        paa_elab_com_doc = paa_factory.create(
            periodo_paa=periodo, associacao=assoc2, status=PaaStatusEnum.EM_ELABORACAO.name
        )
        documento_paa_factory.create(
            paa=paa_elab_com_doc,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        # PAA em elaboracao sem doc
        assoc3 = associacao_factory.create()
        paa_elab_sem_doc = paa_factory.create(
            periodo_paa=periodo, associacao=assoc3, status=PaaStatusEnum.EM_ELABORACAO.name
        )

        resultado = _qs().paas_gerados_parcialmente()
        assert resultado.count() == 2
        pks = set(resultado.values_list('pk', flat=True))
        assert pks == {paa_retificacao.pk, paa_elab_com_doc.pk}

        resultado_qs = _qs().paas_gerados_parcialmente()
        assert resultado_qs.count() == 2
        pks_qs = set(resultado_qs.values_list('pk', flat=True))
        assert pks_qs == {paa_retificacao.pk, paa_elab_com_doc.pk}

        resultado_em_elaboracao = _qs().paas_em_elaboracao()
        assert resultado_em_elaboracao.count() == 1
        pks_qs_sem_docs = set(resultado_em_elaboracao.values_list('pk', flat=True))
        assert pks_qs_sem_docs == {paa_elab_sem_doc.pk}

    def test_filtra_somente_em_elaboracao(
        self, paa_factory, documento_paa_factory, ata_paa_factory, periodo_paa_factory, associacao_factory
    ):
        periodo = periodo_paa_factory.create()

        # PAA gerado (nao deve aparecer)
        assoc1 = associacao_factory.create()
        paa_gerado = paa_factory.create(
            periodo_paa=periodo, associacao=assoc1, status=PaaStatusEnum.GERADO.name
        )
        documento_paa_factory.create(
            paa=paa_gerado,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )
        ata_paa_factory.create(paa=paa_gerado, status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO)

        # PAA em elaboracao sem doc (deve aparecer)
        assoc2 = associacao_factory.create()
        paa_elab = paa_factory.create(
            periodo_paa=periodo, associacao=assoc2, status=PaaStatusEnum.EM_ELABORACAO.name
        )

        resultado = _qs().filter_por_status_geracao(PaaStatusAndamentoEnum.EM_ELABORACAO.name)
        assert resultado.count() == 1
        assert resultado.first().pk == paa_elab.pk

        resultado_qs = _qs().paas_em_elaboracao()
        assert resultado_qs.count() == 1
        assert resultado_qs.first().pk == paa_elab.pk
