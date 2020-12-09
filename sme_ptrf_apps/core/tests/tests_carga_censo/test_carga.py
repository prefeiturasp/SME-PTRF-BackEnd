import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.carga_censo import carrega_censo
from sme_ptrf_apps.core.models import Censo

from sme_ptrf_apps.core.models.arquivo import (
    CARGA_CENSO,
    DELIMITADOR_PONTO_VIRGULA, 
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv', 
        bytes(f"""Código EOL,Quantidade Alunos,Ano\n000108,20,2020\n123456,34,2020""", encoding="utf-8"))

@pytest.fixture
def arquivoComErro():
    return SimpleUploadedFile(
        f'arquivo.csv', 
        bytes(f"""Código EOL,Quantidade Alunos,Ano\n000108,20,2020\n123980,34,2020\n,,""", encoding="utf-8"))

@pytest.fixture
def arquivoCarga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_censo',
        conteudo=arquivo,
        tipo_carga=CARGA_CENSO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )

@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_censo',
        conteudo=arquivo,
        tipo_carga=CARGA_CENSO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaComErro(arquivoComErro):
    return baker.make(
        'Arquivo',
        identificador='carga_censo',
        conteudo=arquivoComErro,
        tipo_carga=CARGA_CENSO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_censo(arquivoCarga)
    assert arquivoCarga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_processada_com_erro(arquivoCargaVirgula, unidade):
    assert not Censo.objects.exists()
    carrega_censo(arquivoCargaVirgula)
    assert arquivoCargaVirgula.log == """\nUnidade Não encontrada para código eol (000108) na linha 1.\nImportadas 1 dados de censo. Erro na importação de 1 dados do censo."""
    assert arquivoCargaVirgula.status == PROCESSADO_COM_ERRO
    assert Censo.objects.exists()


def test_carga_com_erro(arquivoCargaVirgulaComErro, unidade):
    assert not Censo.objects.exists()
    carrega_censo(arquivoCargaVirgulaComErro)
    assert arquivoCargaVirgulaComErro.log == """\nUnidade Não encontrada para código eol (000108) na linha 1.\nUnidade Não encontrada para código eol (123980) na linha 2.\nImportadas 0 dados de censo. Erro na importação de 2 dados do censo."""
    assert arquivoCargaVirgulaComErro.status == ERRO
    assert not Censo.objects.exists()
