import json
import pytest
from unittest.mock import patch
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_nao_pode_gerar_final_quando_previa_em_processamento(
        jwt_authenticated_client_sme, flag_paa, documento_paa_factory, paa_factory):
    paa = paa_factory()
    documento_paa_factory(paa=paa, versao="PREVIA", status_geracao="EM_PROCESSAMENTO")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json',
                                                 data=json.dumps({"confirmar": 1}))
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Há uma geração de prévia em processamento. Aguarde a conclusão para gerar a versão final."
    ) in result["mensagem"]


def test_nao_pode_gerar_final_quando_documento_final_existe(jwt_authenticated_client_sme, flag_paa,
                                                            documento_paa_factory):
    documento = documento_paa_factory(versao="FINAL", status_geracao="CONCLUIDO")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{documento.paa.uuid}/gerar-documento/',
                                                 content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["mensagem"] == "Não é possível gerar o documento. Já existe uma versão final gerada."


def test_retorna_erros_de_validacao_geracao_final(jwt_authenticated_client_sme, flag_paa, paa_factory):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    msg = response.data["mensagem"]

    assert "É necessário indicar pelo menos um objetivo" in msg
    assert "É necessário inserir o texto de introdução" in msg
    assert "É necessário inserir o texto de conclusão" in msg


def test_iniciar_geracao_final_com_sucesso(jwt_authenticated_client_sme, flag_paa, paa_factory, objetivo_paa_factory,
                                           atividade_estatutaria_paa_factory):
    objetivo = objetivo_paa_factory()
    paa = paa_factory(texto_introducao="Um texto introducao", texto_conclusao="Um texto conclusao")
    paa.objetivos.add(objetivo)
    atividade_estatutaria_paa_factory(paa=paa)

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json',
                                                 data=json.dumps({"confirmar": 1}))

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["mensagem"] == 'Geração de documento final iniciada'


def test_nao_pode_gerar_previa_quando_documento_final_existe(jwt_authenticated_client_sme, flag_paa,
                                                             documento_paa_factory, paa_factory):
    paa = paa_factory()
    documento_paa_factory(paa=paa, versao="FINAL")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-previa-documento/',
                                                 content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["mensagem"] == "Não é possível gerar o documento. Já existe uma versão final gerada."


def test_iniciar_geracao_previa_com_sucesso(jwt_authenticated_client_sme, flag_paa, paa_factory):
    from sme_ptrf_apps.paa.models import DocumentoPaa

    paa = paa_factory()

    with patch('sme_ptrf_apps.paa.api.views.paa_viewset.gerar_previa_documento_paa_async.apply_async'):
        response = jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/gerar-previa-documento/',
            content_type='application/json',
        )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["mensagem"] == 'Geração de documento prévia iniciada'

    documento_previa = paa.documentopaa_set.filter(versao=DocumentoPaa.VersaoChoices.PREVIA).first()
    assert documento_previa is not None
    assert documento_previa.status_geracao == DocumentoPaa.StatusChoices.EM_PROCESSAMENTO


def test_nao_pode_gerar_previa_quando_previa_em_processamento(jwt_authenticated_client_sme, flag_paa,
                                                              documento_paa_factory, paa_factory):
    paa = paa_factory()
    documento_paa_factory(paa=paa, versao="PREVIA", status_geracao="EM_PROCESSAMENTO")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-previa-documento/',
                                                 content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Há uma geração de prévia em processamento. Aguarde a conclusão para gerar a versão final."
    ) in result["mensagem"]


def test_gerar_documento_final_bloqueado_apos_iniciar_previa_na_api(
        jwt_authenticated_client_sme, flag_paa, paa_factory, objetivo_paa_factory,
        atividade_estatutaria_paa_factory):
    objetivo = objetivo_paa_factory()
    paa = paa_factory(texto_introducao="Intro", texto_conclusao="Conclusao")
    paa.objetivos.add(objetivo)
    atividade_estatutaria_paa_factory(paa=paa)

    with patch('sme_ptrf_apps.paa.api.views.paa_viewset.gerar_previa_documento_paa_async.apply_async'):
        jwt_authenticated_client_sme.post(
            f'/api/paa/{paa.uuid}/gerar-previa-documento/',
            content_type='application/json',
        )

    response = jwt_authenticated_client_sme.post(
        f'/api/paa/{paa.uuid}/gerar-documento/',
        content_type='application/json',
        data=json.dumps({"confirmar": 1}),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Há uma geração de prévia em processamento. Aguarde a conclusão para gerar a versão final."
    ) in response.json()["mensagem"]


def test_gerar_documento_sem_confirmacao(jwt_authenticated_client_sme, flag_paa, paa_factory,
                                         objetivo_paa_factory, atividade_estatutaria_paa_factory):
    objetivo = objetivo_paa_factory()
    paa = paa_factory(texto_introducao="Intro", texto_conclusao="Conclusao")
    paa.objetivos.add(objetivo)
    atividade_estatutaria_paa_factory(paa=paa)

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json',
                                                 data=json.dumps({}))

    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'confirmar' in result
