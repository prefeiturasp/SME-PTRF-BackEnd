import pytest
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import DocumentoPaa, Paa
from sme_ptrf_apps.paa.models.documento_paa import obter_documento_final_por_retificacao
from sme_ptrf_apps.paa.fixtures.factories import DocumentoPaaFactory


@pytest.mark.django_db
def test_obter_documento_final_por_retificacao_sem_paa():
    assert obter_documento_final_por_retificacao(None, False) is None


@pytest.mark.django_db
def test_obter_documento_final_por_retificacao_paa_sem_pk():
    assert obter_documento_final_por_retificacao(Paa(), False) is None


@pytest.mark.django_db
def test_obter_documento_final_por_retificacao_retorna_mais_recente_e_filtra_flag(
    paa_factory, documento_paa_factory, periodo_paa_1, associacao,
):
    paa = paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    d2 = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    assert obter_documento_final_por_retificacao(paa, False).pk == d2.pk
    assert obter_documento_final_por_retificacao(paa, True) is None

    dr = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=True,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    assert obter_documento_final_por_retificacao(paa, True).pk == dr.pk


@pytest.mark.django_db
def test_paa_documento_final_gerado_prefere_documento_original(
    paa_factory, documento_paa_factory, periodo_paa_1, associacao,
):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_1,
        associacao=associacao,
        status=PaaStatusEnum.GERADO.name,
    )
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=True,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    doc_orig = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    assert paa.documento_final.pk == doc_orig.pk


@pytest.mark.django_db
def test_paa_documento_final_em_retificacao_prefere_documento_retificacao(
    paa_factory, documento_paa_factory, periodo_paa_1, associacao,
):
    paa = paa_factory.create(
        periodo_paa=periodo_paa_1,
        associacao=associacao,
        status=PaaStatusEnum.EM_RETIFICACAO.name,
    )
    documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=False,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    doc_ret = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        retificacao=True,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    assert paa.documento_final.pk == doc_ret.pk


@pytest.mark.django_db
def test_create_documento_paa():
    recurso = DocumentoPaaFactory()

    qs = DocumentoPaa.objects.get(id=recurso.id)
    assert qs is not None


@pytest.mark.django_db
def test_str_representation(documento_paa):
    assert f'Documento PAA {DocumentoPaa.VersaoChoices(documento_paa.versao).label} gerado dia' in str(documento_paa)
