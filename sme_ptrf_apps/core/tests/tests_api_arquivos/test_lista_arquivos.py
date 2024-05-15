import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from ...models.arquivo import DELIMITADOR_PONTO_VIRGULA

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_REPASSE_PREVISTO_SME

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


def test_lista_arquivos(jwt_authenticated_client, arquivo_carga):
    response = jwt_authenticated_client.get('/api/arquivos/')
    result = response.json()

    resulta_esperado = [
        {
            'id': arquivo_carga.id,
            'criado_em': arquivo_carga.criado_em.isoformat("T"),
            'alterado_em': arquivo_carga.alterado_em.isoformat("T"),
            'uuid': str(arquivo_carga.uuid),
            'identificador': 'carga_previsao_repasse',
            'conteudo': 'http://testserver/media/arquivo.csv',
            'tipo_carga': 'CARGA_REPASSE_PREVISTO_SME',
            'tipo_delimitador': 'DELIMITADOR_PONTO_VIRGULA',
            'status': 'PENDENTE',
            'log': None,
            'periodo': None,
            'ultima_execucao': None
            }
        ]

    assert result == resulta_esperado
