import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.carga_previsao_repasse import carrega_previsoes_repasses

from ...models import PrevisaoRepasseSme
from ...models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)


from sme_ptrf_apps.core.choices.tipos_carga import CARGA_REPASSE_PREVISTO_SME

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        f'arquivo1.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n123456,Cheque,PTRF,2019.2,99000.98,99000.98,\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivo_processado_com_duas_acoes():
    return SimpleUploadedFile(
        f'arquivo2.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n123456,Cheque,PTRF,2019.2,99000.98,99000.98,\n123456,Cheque,Rolê Cultural,2019.2,1000,2000,""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado_com_duas_acoes(arquivo_processado_com_duas_acoes):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo_processado_com_duas_acoes,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga):
    carrega_previsoes_repasses(arquivo_carga)
    assert arquivo_carga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula):
    carrega_previsoes_repasses(arquivo_carga_virgula)
    msg = """Erro na linha 1: Associação com código eol: 93238 não encontrado.
Importados 0 previsões de repasse. Erro na importação de 1 previsões."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo, associacao, conta_associacao, acao_associacao):
    assert not PrevisaoRepasseSme.objects.exists()
    carrega_previsoes_repasses(arquivo_carga_virgula_processado)
    msg = """Erro na linha 2: Associação com código eol: 93238 não encontrado.
Importados 1 previsões de repasse. Erro na importação de 1 previsões."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == PROCESSADO_COM_ERRO
    assert PrevisaoRepasseSme.objects.exists()


def test_carga_processado_com_sucesso(arquivo_carga_virgula_processado_com_duas_acoes, periodo, associacao,
                                      conta_associacao, acao_associacao, acao_associacao_role_cultural):
    from decimal import Decimal
    assert not PrevisaoRepasseSme.objects.exists()
    carrega_previsoes_repasses(arquivo_carga_virgula_processado_com_duas_acoes)
    msg = """Importados 1 previsões de repasse. Erro na importação de 0 previsões."""
    assert arquivo_carga_virgula_processado_com_duas_acoes.log == msg
    assert arquivo_carga_virgula_processado_com_duas_acoes.status == SUCESSO
    assert len(PrevisaoRepasseSme.objects.all()) == 1
    assert PrevisaoRepasseSme.objects.first().valor_capital == Decimal("101000.98")
