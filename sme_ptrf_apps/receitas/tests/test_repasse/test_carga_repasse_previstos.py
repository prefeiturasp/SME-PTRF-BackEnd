import pytest
import datetime

from sme_ptrf_apps.receitas.services.carga_repasses_previstos import carrega_repasses_previstos
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_REPASSE_PREVISTO

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'2020_01_01_a_2020_06_30_cheque.csv',
        bytes(f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,93238,99000.98,99000.98,,Role Cultural""", encoding="utf-8"))


@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
        bytes(f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,123456,99000.98,99000.98,,Role Cultural\n20,93238,99000.98,99000.98,,Role Cultural""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado):
    return baker.make(
        'Arquivo',
        identificador='2019_01_01_a_2019_11_30_cheque',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga, tipo_conta_cheque):
    carrega_repasses_previstos(arquivo_carga)
    assert arquivo_carga.log == 'Erro ao processar repasses previstos: Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula, tipo_conta_cheque):
    carrega_repasses_previstos(arquivo_carga_virgula)
    msg = """Erro na linha 1: Associação com código eol: 93238 não encontrado.
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


@pytest.fixture
def acao_role_cultural_teste():
    return baker.make('Acao', nome='Role Cultural')


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo, associacao, tipo_receita_repasse,
                                   tipo_conta_cheque, acao_role_cultural, acao_role_cultural_teste):
    carrega_repasses_previstos(arquivo_carga_virgula_processado)
    msg = """Erro na linha 2: Associação com código eol: 93238 não encontrado.
Foram criados 1 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == PROCESSADO_COM_ERRO
