import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.users.services.carga_usuarios import  carrega_usuarios


from sme_ptrf_apps.core.models.arquivo import (
    CARGA_USUARIOS,
    DELIMITADOR_PONTO_VIRGULA, 
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'usuarios.csv', 
        bytes(f"""RF,Visão,Codigo EOL unidade\n7483902,UE,200256\n7483902,DRE,108100\n7210418,UE,200237\n6949215,UE,200188\n8359229,UE,200197""", encoding="utf-8"))

@pytest.fixture
def arquivoProcessado():
    return SimpleUploadedFile(
        f'usuarios_.csv', 
        bytes(f"""RF,Visão,Codigo EOL unidade\n7483902,UE,123456\n7483902,DRE,108100\n7210418,UE,200237\n6949215,UE,200188\n8359229,UE,200197""", encoding="utf-8"))


@pytest.fixture
def arquivoCarga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivo,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivo,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaProcessado(arquivoProcessado):
    return baker.make(
        'Arquivo',
        identificador='carga_usuarios',
        conteudo=arquivoProcessado,
        tipo_carga=CARGA_USUARIOS,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_usuarios(arquivoCarga)
    assert arquivoCarga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_com_erro(arquivoCargaVirgula):
    carrega_usuarios(arquivoCargaVirgula)
    print(arquivoCargaVirgula.log)
    msg = """\nAssociação para o CNPJ UE não encontrado. linha: 1
Associação para o CNPJ DRE não encontrado. linha: 2
Associação para o CNPJ UE não encontrado. linha: 3
Associação para o CNPJ UE não encontrado. linha: 4
Associação para o CNPJ UE não encontrado. linha: 5
Importados 0 usuários. Erro na importação de 5 usuários."""
    assert arquivoCargaVirgula.log == msg
    assert arquivoCargaVirgula.status == ERRO


def test_carga_processado_com_erro(arquivoCargaVirgulaProcessado, unidade):
    carrega_usuarios(arquivoCargaVirgulaProcessado)
    print(arquivoCargaVirgulaProcessado.log)
    msg = """\nAssociação para o CNPJ DRE não encontrado. linha: 2
Associação para o CNPJ UE não encontrado. linha: 3
Associação para o CNPJ UE não encontrado. linha: 4
Associação para o CNPJ UE não encontrado. linha: 5
Importados 1 usuários. Erro na importação de 4 usuários."""
    assert arquivoCargaVirgulaProcessado.log == msg
    assert arquivoCargaVirgulaProcessado.status == PROCESSADO_COM_ERRO
