import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.carga_associacoes import carrega_associacoes

from ...models import Associacao
from ...models.arquivo import (
    CARGA_ASSOCIACOES,
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código EOL UE;Nome UE;Código EOL DRE;Nome da DRE UE;Sigla DRE;Nome da associação;CNPJ da associação;RF Presidente Diretoria;Nome Presidente Diretoria;RF Presidente Conselho Fiscal;Nome Presidente Conselho Fiscal
000086;EMEI PAULO CAMILHIER FLORENCANO;108500;GUAIANASES;G;EMEI PAULO CAMILHIER FLORENÇANO;1142145000190;;;;
000094;EMEI VICENTE PAULO DA SILVA;108400;FREGUESIA/BRASILANDIA;FO;EMEI VICENTE PAULO DA SILVA;6139086000;;;;
000108;"EMEF JOSE ERMIRIO DE MORAIS; SEN.";109300;SAO MIGUEL;MP;EMEF SEN JOSÉ ERMINIO DE MORAIS;1095757000179;;;;""", encoding="utf-8"))


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
    carrega_associacoes(arquivo_carga)
    assert arquivo_carga.log == 'Formato definido (DELIMITADOR_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_PONTO_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_processada_com_erro(arquivo_carga_ponto_virgula):
    assert not Associacao.objects.exists()
    carrega_associacoes(arquivo_carga_ponto_virgula)
    msg = """\nCNPJ inválido (6139086000) na linha 2. Associação não criada.\nImportadas 2 associações. Erro na importação de 1 associações."""
    assert arquivo_carga_ponto_virgula.log == msg
    assert arquivo_carga_ponto_virgula.status == PROCESSADO_COM_ERRO
    assert Associacao.objects.exists()
