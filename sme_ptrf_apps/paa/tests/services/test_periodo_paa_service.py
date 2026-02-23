import pytest
from model_bakery import baker

from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models.ata_paa import AtaPaa
from sme_ptrf_apps.paa.fixtures.factories import AtaPaaFactory, DocumentoPaaFactory
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa
from sme_ptrf_apps.paa.services.periodo_paa_service import PeriodoPaaService


def _cria_paa_gerado(paa_factory, periodo_paa, associacao):
    """
    Cria um PAA que satisfaz todos os critérios de 'gerado':
    - status = GERADO
    - DocumentoPaa com versão FINAL e status_geracao = CONCLUIDO
    - AtaPaa com status_geracao_pdf = CONCLUIDO
    """
    paa = paa_factory.create(
        periodo_paa=periodo_paa,
        associacao=associacao,
        status=PaaStatusEnum.GERADO.name,
    )
    DocumentoPaaFactory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    AtaPaaFactory.create(
        paa=paa,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )
    return paa


@pytest.mark.django_db
class TestExistePaasGeradosNoPeriodo:
    """Testes para o método existe_paas_gerados_no_periodo"""

    def test_retorna_true_quando_existe_paa_gerado_no_periodo(
        self,
        periodo_paa_1,
        associacao,
        paa_factory,
    ):
        """Deve retornar True quando existe PAA com status GERADO, documento final e ata concluídos"""
        _cria_paa_gerado(paa_factory, periodo_paa_1, associacao)

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is True

    def test_retorna_false_quando_nao_existe_paa_no_periodo(self, periodo_paa_1):
        """Deve retornar False quando não existe nenhum PAA no período"""
        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is False

    def test_retorna_false_quando_paa_nao_esta_com_status_gerado(
        self,
        periodo_paa_1,
        associacao,
        paa_factory,
        documento_paa_factory,
        ata_paa_factory,
    ):
        """Deve retornar False quando PAA está em elaboração, mesmo com documento final e ata concluídos"""
        paa = paa_factory.create(
            periodo_paa=periodo_paa_1,
            associacao=associacao,
            status=PaaStatusEnum.EM_ELABORACAO.name,
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

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is False

    def test_retorna_false_quando_paa_gerado_sem_documento_final_concluido(
        self,
        periodo_paa_1,
        associacao,
        paa_factory,
        ata_paa_factory,
    ):
        """Deve retornar False quando PAA tem status GERADO mas sem documento final concluído"""
        paa = paa_factory.create(
            periodo_paa=periodo_paa_1,
            associacao=associacao,
            status=PaaStatusEnum.GERADO.name,
        )
        ata_paa_factory.create(
            paa=paa,
            status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        )

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is False

    def test_retorna_false_quando_paa_gerado_sem_ata_concluida(
        self,
        periodo_paa_1,
        associacao,
        paa_factory,
        documento_paa_factory,
    ):
        """Deve retornar False quando PAA tem status GERADO e documento final, mas sem ata concluída"""
        paa = paa_factory.create(
            periodo_paa=periodo_paa_1,
            associacao=associacao,
            status=PaaStatusEnum.GERADO.name,
        )
        documento_paa_factory.create(
            paa=paa,
            versao=DocumentoPaa.VersaoChoices.FINAL,
            status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        )

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is False

    def test_retorna_false_quando_paa_gerado_esta_em_outro_periodo(
        self,
        periodo_paa_1,
        periodo_paa_2,
        associacao,
        paa_factory,
    ):
        """Deve retornar False quando o PAA gerado pertence a outro período"""
        _cria_paa_gerado(paa_factory, periodo_paa_2, associacao)

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is False

    def test_retorna_true_com_multiplos_paas_gerados_no_periodo(
        self,
        periodo_paa_1,
        paa_factory,
    ):
        """Deve retornar True quando existem múltiplos PAAs gerados no período"""
        associacao_1 = baker.make('Associacao')
        associacao_2 = baker.make('Associacao')

        _cria_paa_gerado(paa_factory, periodo_paa_1, associacao_1)
        _cria_paa_gerado(paa_factory, periodo_paa_1, associacao_2)

        service = PeriodoPaaService(periodo_paa=periodo_paa_1)

        assert service.existe_paas_gerados_no_periodo() is True
