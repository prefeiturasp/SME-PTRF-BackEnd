import pytest
from django.contrib.admin.sites import site
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from sme_ptrf_apps.paa.models import DocumentoPaa, AtaPaa
from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.core.admin import PrestacaoContaAdmin


@pytest.fixture
def prestacao_conta_admin():
    return PrestacaoContaAdmin(model=PrestacaoConta, admin_site=site)


# =========================
# REQUEST HELPER BASE
# =========================
@pytest.fixture
def api_request_factory():
    from rest_framework.test import APIRequestFactory
    return APIRequestFactory()


@pytest.fixture
def prestacao_uuid_view():
    from sme_ptrf_apps.core.api.views.prestacoes_contas_viewset import PrestacoesContasViewSet
    return PrestacoesContasViewSet.as_view({"get": "obter_documentos_paa"})


@pytest.fixture
def autenticar():
    from rest_framework.test import force_authenticate

    def _auth(request, user):
        force_authenticate(request, user=user)
        return request

    return _auth


# =========================
# PERÍODO COMPATÍVEL
# =========================
@pytest.fixture
def periodo_paa_compativel(periodo_paa_factory, prestacao_conta):
    data_inicio = prestacao_conta.periodo.data_inicio_prestacao_contas
    data_fim = date(data_inicio.year + 1, 12, 31)

    return periodo_paa_factory.create(
        data_inicial=data_inicio,
        data_final=data_fim,
    )


# =========================
# PAA BASE
# =========================
@pytest.fixture
def paa_base(paa_factory, prestacao_conta, periodo_paa_compativel):
    return paa_factory.create(
        associacao=prestacao_conta.associacao,
        periodo_paa=periodo_paa_compativel,
    )


# =========================
# DOCUMENTO PAA
# =========================
@pytest.fixture
def documento_paa_com_arquivo(paa_base, documento_paa_factory):
    arquivo = SimpleUploadedFile(
        "documento-paa.pdf",
        b"%PDF-1.4 fake pdf",
        content_type="application/pdf",
    )

    return documento_paa_factory.create(
        paa=paa_base,
        arquivo_pdf=arquivo,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )


@pytest.fixture
def documento_paa_sem_arquivo(paa_base, documento_paa_factory):
    return documento_paa_factory.create(
        paa=paa_base,
        arquivo_pdf=None,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )


# =========================
# ATA PAA
# =========================
@pytest.fixture
def ata_apresentacao(paa_base, ata_paa_factory):
    return ata_paa_factory.create(
        paa=paa_base,
        tipo_ata=AtaPaa.ATA_APRESENTACAO,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
        previa=False,
    )
