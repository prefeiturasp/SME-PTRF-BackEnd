import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.users.services.carga_usuarios import  carrega_usuarios


from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_USUARIOS

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'usuarios.csv',
        bytes(f"""RF,Visão,Codigo EOL unidade\n7483902,UE,200256\n7483902,DRE,108100\n7210418,UE,200237\n6949215,UE,200188\n8359229,UE,200197""", encoding="utf-8"))

@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        f'usuarios_.csv',
        bytes(f"""RF,Visão,Codigo EOL unidade\n7483902,UE,123456\n7483902,DRE,108100\n7210418,UE,200237\n6949215,UE,200188\n8359229,UE,200197""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivo,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivo,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga):
    carrega_usuarios(arquivo_carga)
    assert arquivo_carga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula):
    carrega_usuarios(arquivo_carga_virgula)
    msg = """\nAssociação para o código eol 200256 não encontrado. linha: 1
Associação para o código eol 108100 não encontrado. linha: 2
Associação para o código eol 200237 não encontrado. linha: 3
Associação para o código eol 200188 não encontrado. linha: 4
Associação para o código eol 200197 não encontrado. linha: 5
Importados 0 usuários. Erro na importação de 5 usuários."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, unidade):
    carrega_usuarios(arquivo_carga_virgula_processado)
    msg = """\nAssociação para o código eol 108100 não encontrado. linha: 2
Associação para o código eol 200237 não encontrado. linha: 3
Associação para o código eol 200188 não encontrado. linha: 4
Associação para o código eol 200197 não encontrado. linha: 5
Importados 1 usuários. Erro na importação de 4 usuários."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == PROCESSADO_COM_ERRO
