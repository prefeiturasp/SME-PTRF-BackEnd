import pytest
import datetime

from sme_ptrf_apps.receitas.services.carga_repasses_previstos import carrega_repasses_previstos
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.models.arquivo import (
    CARGA_REPASSE_PREVISTO,
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'2020_01_01_a_2020_06_30_cheque.csv',
        bytes(f"""Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n93238,99000.98,99000.98,,Role Cultural,02/01/2020,2020.u""", encoding="utf-8"))


@pytest.fixture
def arquivoProcessado():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv', 
        bytes(f"""Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n123456,99000.98,99000.98,,Role Cultural,02/04/2019,2019.2\n93238,99000.98,99000.98,,Role Cultural,02/01/2020,2020.u""", encoding="utf-8"))


@pytest.fixture
def arquivoCarga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaProcessado(arquivoProcessado):
    return baker.make(
        'Arquivo',
        identificador='2019_01_01_a_2019_11_30_cheque',
        conteudo=arquivoProcessado,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_repasses_previstos(arquivoCarga)
    assert arquivoCarga.log == 'Erro ao processar repasses previstos: Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_com_erro(arquivoCargaVirgula):
    carrega_repasses_previstos(arquivoCargaVirgula)
    msg = """Erro na linha 1: Associação com código eol: 93238 não encontrado.
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivoCargaVirgula.log == msg
    assert arquivoCargaVirgula.status == ERRO


def test_carga_processado_com_erro(arquivoCargaVirgulaProcessado, periodo, associacao, tipo_receita_repasse):
    carrega_repasses_previstos(arquivoCargaVirgulaProcessado)
    msg = """Erro na linha 2: Associação com código eol: 93238 não encontrado.
Foram criados 1 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivoCargaVirgulaProcessado.log == msg
    assert arquivoCargaVirgulaProcessado.status == PROCESSADO_COM_ERRO
