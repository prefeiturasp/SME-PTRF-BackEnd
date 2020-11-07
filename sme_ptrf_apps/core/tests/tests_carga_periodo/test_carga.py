import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.periodo_inicial import  carrega_periodo_inicial


from sme_ptrf_apps.core.models.arquivo import (
    CARGA_PERIODO_INICIAL,
    DELIMITADOR_PONTO_VIRGULA, 
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'periodos_iniciais.csv', 
        bytes(f"""Código eol,periodo\n000256,2019.1\n00094,2019.1""", encoding="utf-8"))

@pytest.fixture
def arquivoProcessado():
    return SimpleUploadedFile(
        f'periodos_iniciais.csv', 
        bytes(f"""Código eol,periodo\n123456,2019.2\n00094,2019.1""", encoding="utf-8"))

@pytest.fixture
def arquivoCarga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivo,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivo,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )

@pytest.fixture
def arquivoCargaVirgulaProcessado(arquivoProcessado):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivoProcessado,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )

def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_periodo_inicial(arquivoCarga)
    assert arquivoCarga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_com_erro(arquivoCargaVirgula):
    carrega_periodo_inicial(arquivoCargaVirgula)
    msg = """\nAssociação (000256) não encontrado. Linha: 1
Associação (00094) não encontrado. Linha: 2
Importados 0 períodos iniciais. Erro na importação de 2 períodos iniciais."""
    assert arquivoCargaVirgula.log == msg
    assert arquivoCargaVirgula.status == ERRO


def test_carga_processado_com_erro(arquivoCargaVirgulaProcessado, periodo, associacao):
    carrega_periodo_inicial(arquivoCargaVirgulaProcessado)
    msg = """\nAssociação (00094) não encontrado. Linha: 2
Importados 1 períodos iniciais. Erro na importação de 1 períodos iniciais."""
    assert arquivoCargaVirgulaProcessado.log == msg
    assert arquivoCargaVirgulaProcessado.status == PROCESSADO_COM_ERRO
