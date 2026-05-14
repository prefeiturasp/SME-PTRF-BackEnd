import pytest
from datetime import date
from django.core.files.base import ContentFile
from freezegun import freeze_time
from rest_framework import status
from sme_ptrf_apps.paa.choices import StatusChoices
from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import AtaPaa, DocumentoPaa

pytestmark = pytest.mark.django_db


def test_carrega_paas_anteriores(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):

    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024)
    # considerar mesma associacao
    paa_2025 = paa_factory.create(periodo_paa=periodo_2025, associacao=paa_2024.associacao)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa_2025.uuid)}/paas-anteriores/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0]['periodo_paa_objeto']['referencia'] == "Periodo 2024"
    assert result[0]['associacao'] == str(paa_2024.associacao.uuid)


def test_action_resumo_prioridades(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):

    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2025 = paa_factory.create(periodo_paa=periodo_2025)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(paa_2025.uuid)}/resumo-prioridades/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 3
    assert result[0]['key'] == 'PTRF'
    assert result[1]['key'] == 'PDDE'
    assert result[2]['key'] == 'OUTRO_RECURSO'


def test_get_objetivos_disponiveis(jwt_authenticated_client_sme, flag_paa, objetivo_paa_factory):

    objetivo_1 = objetivo_paa_factory()

    objetivo_paa_factory()

    response = jwt_authenticated_client_sme.get(f"/api/paa/{str(objetivo_1.paa.uuid)}/objetivos/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_atividades_estatutarias_disponiveis(jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_factory):

    atividade_1 = atividade_estatutaria_factory(status=StatusChoices.ATIVO)
    atividade_estatutaria_factory(status=StatusChoices.ATIVO)

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(atividade_1.paa.uuid)}/atividades-estatutarias-disponiveis/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_atividades_estatutarias_previstas(
    jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_paa_factory,
):

    atividade = atividade_estatutaria_paa_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(atividade.paa.uuid)}/atividades-estatutarias-previstas/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_get_recursos_proprios_previstos(jwt_authenticated_client_sme, flag_paa, recurso_proprio_paa_factory):

    recurso = recurso_proprio_paa_factory()

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/{str(recurso.paa.uuid)}/recursos-proprios-previstos/")

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


@freeze_time('2025-06-15')
def test_get_paa_vigente_e_anteriores(
    jwt_authenticated_client_sme,
    flag_paa,
    paa_factory,
    periodo_paa_factory,
    ata_paa_factory,
    documento_paa_factory,
):
    periodo_2024 = periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))
    periodo_2025 = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))

    paa_2024 = paa_factory.create(periodo_paa=periodo_2024, status=PaaStatusEnum.GERADO.name)

    ata_paa_factory.create(
        paa=paa_2024,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )
    documento_paa_factory.create(
        paa=paa_2024,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )

    paa_2025 = paa_factory.create(
        periodo_paa=periodo_2025,
        associacao=paa_2024.associacao,
        status=PaaStatusEnum.GERADO.name,
    )

    ata_paa_factory.create(
        paa=paa_2025,
        status_geracao_pdf=AtaPaa.STATUS_CONCLUIDO,
    )

    documento_paa_factory.create(
        paa=paa_2025,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
    )
    response = jwt_authenticated_client_sme.get(
        f"/api/paa/paa-vigente-e-anteriores/?associacao_uuid={paa_2025.associacao.uuid}"
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result['vigente']['uuid'] == str(paa_2025.uuid)
    assert result['vigente']['referencia'] == 'Periodo 2025'
    assert result['vigente']['esta_em_retificacao'] is False
    assert result['vigente']['retificacao'] is None
    assert result['vigente']['original']['documento']['status']['status_geracao'] == 'CONCLUIDO'
    assert result['vigente']['original']['ata']['status']['status_geracao'] == AtaPaa.STATUS_CONCLUIDO
    assert result['vigente']['original']['ata']['apresenta_botoes_acao'] is False
    assert len(result['anteriores']) == 1
    assert result['anteriores'][0]['uuid'] == str(paa_2024.uuid)
    assert result['anteriores'][0]['referencia'] == 'Periodo 2024'
    assert result['anteriores'][0]['original']['ata']['apresenta_botoes_acao'] is False


@freeze_time('2025-06-15')
def test_get_documento_final_com_query_retificacao(
    jwt_authenticated_client_sme,
    flag_paa,
    paa_factory,
    periodo_paa_factory,
    documento_paa_factory,
):
    periodo_2025 = periodo_paa_factory.create(
        referencia='Periodo 2025',
        data_inicial=date(2025, 1, 1),
        data_final=date(2025, 12, 31),
    )
    paa = paa_factory.create(periodo_paa=periodo_2025, status=PaaStatusEnum.GERADO.name)
    pdf_orig = b'%PDF-1.4 orig'
    pdf_ret = b'%PDF-1.4 ret'

    doc_orig = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=False,
    )
    doc_orig.arquivo_pdf.save('orig.pdf', ContentFile(pdf_orig), save=True)

    doc_ret = documento_paa_factory.create(
        paa=paa,
        versao=DocumentoPaa.VersaoChoices.FINAL,
        status_geracao=DocumentoPaa.StatusChoices.CONCLUIDO,
        retificacao=True,
    )
    doc_ret.arquivo_pdf.save('ret.pdf', ContentFile(pdf_ret), save=True)

    r_false = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/documento-final/?retificacao=false'
    )
    r_true = jwt_authenticated_client_sme.get(
        f'/api/paa/{paa.uuid}/documento-final/?retificacao=true'
    )

    assert r_false.status_code == status.HTTP_200_OK
    assert r_true.status_code == status.HTTP_200_OK
    assert r_false.content == pdf_orig
    assert r_true.content == pdf_ret


@freeze_time('2026-01-01')
def test_get_paa_vigente_e_anteriores_sem_periodo(
    jwt_authenticated_client_sme,
    flag_paa,
    associacao,
    periodo_paa_factory,
):
    periodo_paa_factory.create(
        referencia="Periodo 2024", data_inicial=date(2024, 1, 1), data_final=date(2024, 12, 31))

    response = jwt_authenticated_client_sme.get(
        f"/api/paa/paa-vigente-e-anteriores/?associacao_uuid={associacao.uuid}"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_paa_vigente_e_anteriores_sem_associacao_uuid(
    jwt_authenticated_client_sme,
    flag_paa,
):
    response = jwt_authenticated_client_sme.get("/api/paa/paa-vigente-e-anteriores/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'parametros_requeridos'


def test_get_paa_vigente_e_anteriores_associacao_nao_encontrada(
    jwt_authenticated_client_sme,
    flag_paa,
):
    response = jwt_authenticated_client_sme.get(
        "/api/paa/paa-vigente-e-anteriores/?associacao_uuid=00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['erro'] == 'Objeto não encontrado.'


def test_get_receitas_previstas(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):
    periodo = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))
    paa = paa_factory.create(periodo_paa=periodo)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/receitas-previstas/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


def test_get_plano_orcamentario(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):
    periodo = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))
    paa = paa_factory.create(periodo_paa=periodo)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/plano-orcamentario/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, dict)


def test_get_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa, paa_factory, periodo_paa_factory):
    periodo = periodo_paa_factory.create(
        referencia="Periodo 2025", data_inicial=date(2025, 1, 1), data_final=date(2025, 12, 31))
    paa = paa_factory.create(periodo_paa=periodo)

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/outros-recursos-do-periodo/")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)


def test_get_documento_previa_nao_gerado(jwt_authenticated_client_sme, flag_paa, paa_factory):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/documento-previa/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['mensagem'] == 'Documento prévia não gerado'


def test_get_documento_previa_nao_concluido(jwt_authenticated_client_sme, flag_paa, paa_factory,
                                            documento_paa_factory):
    paa = paa_factory()
    documento_paa_factory.create(paa=paa, versao='PREVIA', status_geracao='NAO_GERADO')

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/documento-previa/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['mensagem'] == 'Documento prévia não concluído'


def test_get_status_geracao_pendente(jwt_authenticated_client_sme, flag_paa, paa_factory):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/status-geracao/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mensagem'] == 'Documento pendente de geração'


def test_get_status_geracao_com_documento_previa(jwt_authenticated_client_sme, flag_paa, paa_factory,
                                                 documento_paa_factory):
    paa = paa_factory()
    documento_paa_factory.create(paa=paa, versao='PREVIA', status_geracao='EM_PROCESSAMENTO')

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/status-geracao/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['versao'] == 'PREVIA'
    assert response.data['status'] == 'EM_PROCESSAMENTO'


def test_get_status_geracao_com_documento_final(jwt_authenticated_client_sme, flag_paa, paa_factory,
                                                documento_paa_factory):
    paa = paa_factory()
    documento_paa_factory.create(paa=paa, versao='FINAL', status_geracao='CONCLUIDO')

    response = jwt_authenticated_client_sme.get(f"/api/paa/{paa.uuid}/status-geracao/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data['versao'] == 'FINAL'
    assert response.data['status'] == 'CONCLUIDO'
