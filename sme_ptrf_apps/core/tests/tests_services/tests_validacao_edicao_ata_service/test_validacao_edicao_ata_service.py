import pytest

from sme_ptrf_apps.core.models import Ata, PrestacaoConta
from sme_ptrf_apps.core.services.validacao_edicao_ata_service import validar_edicao_ata_pc

pytestmark = pytest.mark.django_db


class TestValidarEdicaoAtaPc:
    def test_bloqueia_edicao_ata_apresentacao_com_pdf_concluido_quando_pc_recebida(
        self, ata_factory, prestacao_conta_factory,
    ):
        prestacao_conta = prestacao_conta_factory(status=PrestacaoConta.STATUS_RECEBIDA)
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            prestacao_conta=prestacao_conta,
            associacao=prestacao_conta.associacao,
            periodo=prestacao_conta.periodo,
            status_geracao_pdf=Ata.STATUS_CONCLUIDO,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is False
        assert 'retificação' in resultado['mensagem'].lower()

    def test_bloqueia_edicao_ata_apresentacao_com_pdf_gerado_previamente_quando_pc_em_analise(
        self, ata_factory, prestacao_conta_factory,
    ):
        prestacao_conta = prestacao_conta_factory(status=PrestacaoConta.STATUS_EM_ANALISE)
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            prestacao_conta=prestacao_conta,
            associacao=prestacao_conta.associacao,
            periodo=prestacao_conta.periodo,
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
            pdf_gerado_previamente=True,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is False
        assert 'retificação' in resultado['mensagem'].lower()

    def test_permite_edicao_ata_apresentacao_com_pdf_concluido_quando_pc_nao_recebida(
        self, ata_factory, prestacao_conta_factory,
    ):
        prestacao_conta = prestacao_conta_factory(status=PrestacaoConta.STATUS_NAO_RECEBIDA)
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            prestacao_conta=prestacao_conta,
            associacao=prestacao_conta.associacao,
            periodo=prestacao_conta.periodo,
            status_geracao_pdf=Ata.STATUS_CONCLUIDO,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is True

    def test_permite_edicao_ata_apresentacao_com_pdf_gerado_previamente_quando_pc_nao_apresentada(
        self, ata_factory, prestacao_conta_factory,
    ):
        prestacao_conta = prestacao_conta_factory(status=PrestacaoConta.STATUS_NAO_APRESENTADA)
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            prestacao_conta=prestacao_conta,
            associacao=prestacao_conta.associacao,
            periodo=prestacao_conta.periodo,
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
            pdf_gerado_previamente=True,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is True

    def test_permite_edicao_ata_apresentacao_sem_pdf(self, ata_factory):
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
            pdf_gerado_previamente=False,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is True

    def test_bloqueia_edicao_ata_apresentacao_durante_retificacao(
        self, ata_factory, prestacao_conta_devolvida,
    ):
        ata_apresentacao = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            prestacao_conta=prestacao_conta_devolvida,
            associacao=prestacao_conta_devolvida.associacao,
            periodo=prestacao_conta_devolvida.periodo,
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
            pdf_gerado_previamente=False,
        )
        ata_factory(
            tipo_ata=Ata.ATA_RETIFICACAO,
            prestacao_conta=prestacao_conta_devolvida,
            associacao=prestacao_conta_devolvida.associacao,
            periodo=prestacao_conta_devolvida.periodo,
            previa=False,
        )

        resultado = validar_edicao_ata_pc(ata_apresentacao)

        assert resultado['is_valid'] is False
        assert 'apenas a ata de retificação' in resultado['mensagem'].lower()

    def test_permite_edicao_ata_retificacao(self, ata_factory):
        ata = ata_factory(
            tipo_ata=Ata.ATA_RETIFICACAO,
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is True

    def test_bloqueia_edicao_ata_em_processamento(self, ata_factory):
        ata = ata_factory(
            tipo_ata=Ata.ATA_APRESENTACAO,
            status_geracao_pdf=Ata.STATUS_EM_PROCESSAMENTO,
        )

        resultado = validar_edicao_ata_pc(ata)

        assert resultado['is_valid'] is False
        assert 'sendo gerada' in resultado['mensagem'].lower()
