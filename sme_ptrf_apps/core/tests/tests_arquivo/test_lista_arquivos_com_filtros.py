from datetime import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from ...models.arquivo import CARGA_REPASSE_PREVISTO_SME, DELIMITADOR_PONTO_VIRGULA

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivoCarga(arquivo, usuario):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        usuario=usuario,
        ultima_execucao=datetime.strptime('21/01/2021', "%d/%m/%Y")
    )


def test_lista_arquivos_por_identificador(jwt_authenticated_client, arquivoCarga):
    response = jwt_authenticated_client.get('/api/arquivos/?identificador=previsao')
    result = response.json()

    resulta_esperado = [
        {
            'id': arquivoCarga.id,
            'usuario': {
                'id': arquivoCarga.usuario.id,
                'username': arquivoCarga.usuario.username
            },
            'criado_em': arquivoCarga.criado_em.isoformat("T"),
            'alterado_em': arquivoCarga.alterado_em.isoformat("T"),
            'uuid': str(arquivoCarga.uuid),
            'identificador': 'carga_previsao_repasse',
            'conteudo': 'http://testserver/media/arquivo.csv',
            'tipo_carga': 'CARGA_REPASSE_PREVISTO_SME',
            'tipo_delimitador': 'DELIMITADOR_PONTO_VIRGULA',
            'status': 'PENDENTE',
            'log': None,
            'ultima_execucao': arquivoCarga.ultima_execucao.isoformat("T")
        }]

    assert result == resulta_esperado


def test_lista_arquivos_por_status(jwt_authenticated_client, arquivoCarga):
    response = jwt_authenticated_client.get('/api/arquivos/?status=PENDENTE')
    result = response.json()

    resulta_esperado = [
        {
            'id': arquivoCarga.id,
            'usuario': {
                'id': arquivoCarga.usuario.id,
                'username': arquivoCarga.usuario.username
            },
            'criado_em': arquivoCarga.criado_em.isoformat("T"),
            'alterado_em': arquivoCarga.alterado_em.isoformat("T"),
            'uuid': str(arquivoCarga.uuid),
            'identificador': 'carga_previsao_repasse',
            'conteudo': 'http://testserver/media/arquivo.csv',
            'tipo_carga': 'CARGA_REPASSE_PREVISTO_SME',
            'tipo_delimitador': 'DELIMITADOR_PONTO_VIRGULA',
            'status': 'PENDENTE',
            'log': None,
            'ultima_execucao': arquivoCarga.ultima_execucao.isoformat("T")
        }]

    assert result == resulta_esperado


def test_lista_arquivos_por_data_execucao(jwt_authenticated_client, arquivoCarga):
    response = jwt_authenticated_client.get('/api/arquivos/?data_execucao=2021-01-21')
    result = response.json()

    resulta_esperado = [
        {
            'id': arquivoCarga.id,
            'usuario': {
                'id': arquivoCarga.usuario.id,
                'username': arquivoCarga.usuario.username
            },
            'criado_em': arquivoCarga.criado_em.isoformat("T"),
            'alterado_em': arquivoCarga.alterado_em.isoformat("T"),
            'uuid': str(arquivoCarga.uuid),
            'identificador': 'carga_previsao_repasse',
            'conteudo': 'http://testserver/media/arquivo.csv',
            'tipo_carga': 'CARGA_REPASSE_PREVISTO_SME',
            'tipo_delimitador': 'DELIMITADOR_PONTO_VIRGULA',
            'status': 'PENDENTE',
            'log': None,
            'ultima_execucao': arquivoCarga.ultima_execucao.isoformat("T")
        }]

    assert result == resulta_esperado
