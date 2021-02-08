import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.periodo_inicial import carrega_periodo_inicial


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
def arquivo_processado():
    return SimpleUploadedFile(
        f'periodos_iniciais.csv',
        bytes(f"""Código eol,periodo\n123456,2019.2\n00094,2019.1""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivo,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivo,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado):
    return baker.make(
        'Arquivo',
        identificador='carga_periodos_iniciais',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_PERIODO_INICIAL,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga):
    carrega_periodo_inicial(arquivo_carga)
    assert arquivo_carga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula):
    carrega_periodo_inicial(arquivo_carga_virgula)
    msg = """\nAssociação (000256) não encontrado. Linha: 1
Associação (00094) não encontrado. Linha: 2
Importados 0 períodos iniciais. Erro na importação de 2 períodos iniciais."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo, associacao):
    carrega_periodo_inicial(arquivo_carga_virgula_processado)
    msg = """\nAssociação (00094) não encontrado. Linha: 2
Importados 1 períodos iniciais. Erro na importação de 1 períodos iniciais."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == PROCESSADO_COM_ERRO
