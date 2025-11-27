

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_nao_pode_gerar_final_quando_documento_final_existe(jwt_authenticated_client_sme, flag_paa, documento_paa_factory, paa_factory):
    paa = paa_factory()
    documento_paa_factory(paa=paa, versao="FINAL")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["mensagem"] == 'O documento final já foi gerado.'


def test_retorna_erros_de_validacao_geracao_final(jwt_authenticated_client_sme, flag_paa, paa_factory):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    msg = response.data["mensagem"]

    assert "É necessário indicar pelo menos um objetivo" in msg
    assert "É necessário inserir o texto de introdução" in msg
    assert "É necessário inserir o texto de conclusão" in msg
    assert "datas das reuniões" in msg


def test_iniciar_geracao_final_com_sucesso(jwt_authenticated_client_sme, flag_paa, paa_factory, objetivo_paa_factory, atividade_estatutaria_paa_factory):
    objetivo = objetivo_paa_factory()
    paa = paa_factory(texto_introducao="Um texto introducao", texto_conclusao="Um texto conclusao")
    paa.objetivos.add(objetivo)
    atividade_estatutaria_paa_factory(paa=paa)

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-documento/',
                                                 content_type='application/json')

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["mensagem"] == 'Geração de documento final iniciada'


def test_nao_pode_gerar_previa_quando_documento_final_existe(jwt_authenticated_client_sme, flag_paa, documento_paa_factory, paa_factory):
    paa = paa_factory()
    documento_paa_factory(paa=paa, versao="FINAL")

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-previa-documento/',
                                                 content_type='application/json')
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result["mensagem"] == 'O documento final já foi gerado e não é mais possível gerar prévias.'


def test_iniciar_geracao_previa_com_sucesso(jwt_authenticated_client_sme, flag_paa, paa_factory):
    paa = paa_factory()

    response = jwt_authenticated_client_sme.post(f'/api/paa/{paa.uuid}/gerar-previa-documento/',
                                                 content_type='application/json')

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["mensagem"] == 'Geração de documento prévia iniciada'
