import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker
from rest_framework import status

from ...models.arquivo import CARGA_REPASSE_PREVISTO_SME, DELIMITADOR_PONTO_VIRGULA

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
    )


def test_download_arquivo_carga(jwt_authenticated_client, arquivo_carga):
    response = jwt_authenticated_client.get(f'/api/arquivos/{arquivo_carga.uuid}/download/')
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == f'attachment; filename={arquivo_carga.conteudo.name}'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'text/csv'
    assert response.status_code == status.HTTP_200_OK
