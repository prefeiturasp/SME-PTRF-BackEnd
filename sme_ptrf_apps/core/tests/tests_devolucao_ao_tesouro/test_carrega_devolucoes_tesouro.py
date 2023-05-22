import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.carga_devolucoes_tesouro_service import CargaDevolucoesTesouroService


from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_DEVOLUCAO_TESOURO

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'devolucao_tesouro.csv',
        bytes(f"""codigo_eol,nome,pc_id,referencia,despesa_id,numero_documento,data_devolucao,valor_devolucao,tipo_devolucao\n000256;MARIA LUIZA MORETTI GENTILE, PROFA.;139;2021.2;3367;-;14/12/2021;7,75;Pagamento de tarifas bancárias em desacordo com a normativa do Programa""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='devolucao_ao_tesouro',
        conteudo=arquivo,
        tipo_carga=CARGA_DEVOLUCAO_TESOURO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_com_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='devolucao_ao_tesouro',
        conteudo=arquivo,
        tipo_carga=CARGA_DEVOLUCAO_TESOURO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )

def test_carga_com_erro_formatacao(arquivo_carga):
    CargaDevolucoesTesouroService().carrega_devolucoes_tesouro(arquivo_carga)
    assert arquivo_carga.log == """\nLinha:0 Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)\n0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_com_virgula):
    CargaDevolucoesTesouroService().carrega_devolucoes_tesouro(arquivo_carga_com_virgula)
    msg = """\nLinha:1 Houve um erro na carga dessa linha:O id da PC 75;Pagamento de tarifas bancárias em desacordo com a normativa do Programa é inválido. Devolução não criada.\n0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    assert arquivo_carga_com_virgula.log == msg
    assert arquivo_carga_com_virgula.status == ERRO
