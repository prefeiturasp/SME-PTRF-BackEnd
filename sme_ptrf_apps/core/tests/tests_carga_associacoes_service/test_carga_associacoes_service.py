import pytest

from unittest.mock import patch, call

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker

from sme_ptrf_apps.core.services.carga_associacoes_service import CargaAssociacoesService

from ...models import Associacao
from ...models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_ASSOCIACOES

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código EOL UE;Nome da associação;CNPJ da associação
000086;EMEI PAULO CAMILHIER FLORENÇANO;1142145000190
000094;EMEI VICENTE PAULO DA SILVA;6139086000
000108;EMEF SEN JOSÉ ERMINIO DE MORAIS;1095757000179""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_ponto_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga):
    CargaAssociacoesService().carrega_associacoes(arquivo_carga)
    msg = """\nLinha:0 Formato definido (DELIMITADOR_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_PONTO_VIRGULA)\n0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    assert arquivo_carga.log == msg
    assert arquivo_carga.status == ERRO


def __test_carga_processada_com_erro(arquivo_carga_ponto_virgula):
    assert not Associacao.objects.exists()

    api_get_dados_unidade_eol = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.get_dados_unidade_eol'
    with patch(api_get_dados_unidade_eol) as mock_get_dados_unidade_eol:
        mock_get_dados_unidade_eol.return_value = {
            "nome": "22 DE MARCO",
            "tipoUnidade": "ESCOLA",
            "email": "emef22marco@sme.prefeitura.sp.gov.br",
            "telefone": "55130007",
            "tipoLogradouro": "Rua",
            "logradouro": "FRANCISCO SOARES",
            "numero": "51",
            "bairro": "PARQUE REGINA",
            "cep": 5774300,
            "nomeDRE": "DIRETORIA REGIONAL DE EDUCACAO CAMPO LIMPO",
            "siglaDRE": "DRE - CL",
            "codigoDRE": "108200",
            "siglaTipoEscola": "EMEF"

        }

        CargaAssociacoesService().carrega_associacoes(arquivo_carga_ponto_virgula)

    msg = """\nLinha:2 Houve um erro na carga dessa linha:CNPJ inválido (6139086000). Associação não criada.\n2 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    assert arquivo_carga_ponto_virgula.log == msg
    assert arquivo_carga_ponto_virgula.status == PROCESSADO_COM_ERRO
    assert Associacao.objects.exists()
