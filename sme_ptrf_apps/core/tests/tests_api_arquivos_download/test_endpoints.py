import datetime
import json
import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ArquivoDownload

pytestmark = pytest.mark.django_db


def test_lista_arquivos_download(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario)
    arquivo_download_factory.create(usuario=usuario)

    response = jwt_authenticated_client.get('/api/arquivos-download/')
    result = response.json()

    assert len(result) == 2
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_do_usuario(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario)
    arquivo_download_factory.create()

    response = jwt_authenticated_client.get('/api/arquivos-download/')
    result = response.json()

    assert len(result) == 1
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_identificador(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, identificador="teste")
    arquivo_download_factory.create(usuario=usuario)

    response = jwt_authenticated_client.get('/api/arquivos-download/?identificador=tes')
    result = response.json()

    assert len(result) == 1
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_informacoes(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, informacoes="teste")
    arquivo_download_factory.create(usuario=usuario)

    response = jwt_authenticated_client.get('/api/arquivos-download/?identificador=tes')
    result = response.json()

    assert len(result) == 1
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_identificador_ou_informacoes(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, informacoes="teste")
    arquivo_download_factory.create(usuario=usuario, identificador="teste")

    response = jwt_authenticated_client.get('/api/arquivos-download/?identificador=tes')
    result = response.json()

    assert len(result) == 2
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_status(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, status='CONCLUIDO')
    arquivo_download_factory.create(usuario=usuario, status='EM_PROCESSAMENTO')

    response = jwt_authenticated_client.get('/api/arquivos-download/?status=CONCLUIDO')
    result = response.json()

    assert len(result) == 1
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_atualizacao(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, status='CONCLUIDO')
    arquivo_download_factory.create(usuario=usuario, status='EM_PROCESSAMENTO')

    response = jwt_authenticated_client.get(f'/api/arquivos-download/?ultima_atualizacao={datetime.date.today()}')
    result = response.json()

    assert len(result) == 2
    assert response.status_code == status.HTTP_200_OK


def test_lista_arquivos_download_filtro_lido(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, lido=True)
    arquivo_download_factory.create(usuario=usuario, lido=False)

    response = jwt_authenticated_client.get(f'/api/arquivos-download/?lido=true')
    result = response.json()

    assert len(result) == 1
    assert response.status_code == status.HTTP_200_OK


def test_deve_marcar_como_lido(jwt_authenticated_client, arquivo_download_factory, usuario):
    arquivo = arquivo_download_factory.create(usuario=usuario)
    assert arquivo.lido is False

    payload = {
        "lido": True,
        "uuid": f"{arquivo.uuid}"
    }

    response = jwt_authenticated_client.put(
        f'/api/arquivos-download/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    result = response.json()

    arquivo_alterado = ArquivoDownload.by_uuid(arquivo.uuid)
    assert result["mensagem"] == "Arquivo atualizado com sucesso"
    assert arquivo_alterado.lido is True
    assert response.status_code == status.HTTP_200_OK


def test_deve_marcar_como_nao_lido(jwt_authenticated_client, arquivo_download_factory, usuario):
    arquivo = arquivo_download_factory.create(usuario=usuario, lido=True)

    assert arquivo.lido is True

    payload = {
        "lido": False,
        "uuid": f"{arquivo.uuid}"
    }

    response = jwt_authenticated_client.put(
        f'/api/arquivos-download/marcar-lido/', data=json.dumps(payload), content_type='application/json')
    result = response.json()

    arquivo_alterado = ArquivoDownload.by_uuid(arquivo.uuid)
    assert result["mensagem"] == "Arquivo atualizado com sucesso"
    assert arquivo_alterado.lido is False
    assert response.status_code == status.HTTP_200_OK


def test_quantidade_nao_lidos(jwt_authenticated_client, arquivo_download_factory, usuario):

    arquivo_download_factory.create(usuario=usuario, status='CONCLUIDO')
    arquivo_download_factory.create(usuario=usuario, status='CONCLUIDO')
    arquivo_download_factory.create(usuario=usuario, status='CONCLUIDO', lido=True)
    arquivo_download_factory.create(usuario=usuario, status='EM_PROCESSAMENTO')

    response = jwt_authenticated_client.get(f'/api/arquivos-download/quantidade-nao-lidos/')
    result = response.json()

    assert result["quantidade_nao_lidos"] == 2
    assert response.status_code == status.HTTP_200_OK
