import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.services.carga_previsao_repasse import carrega_previsoes_repasses

from ...models import PrevisaoRepasseSme
from ...models.arquivo import (
    CARGA_REPASSE_PREVISTO_SME,
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
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivoProcessado():
    return SimpleUploadedFile(
        f'arquivo1.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n123456,Cheque,PTRF,2019.2,99000.98,99000.98,\n93238,Cheque,Role Cultural,2020.u,99000.98,99000.98,""", encoding="utf-8"))


@pytest.fixture
def arquivoProcessadoComDuasAcoes():
    return SimpleUploadedFile(
        f'arquivo2.csv',
        bytes(f"""Código eol,Conta,Ação,Referência Período, Valor capital,Valor custeio,Valor livre aplicacao\n123456,Cheque,PTRF,2019.2,99000.98,99000.98,\n123456,Cheque,Rolê Cultural,2019.2,1000,2000,""", encoding="utf-8"))


@pytest.fixture
def arquivoCarga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaProcessado(arquivoProcessado):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivoProcessado,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaProcessadoComDuasAcoes(arquivoProcessadoComDuasAcoes):
    return baker.make(
        'Arquivo',
        identificador='carga_previsao_repasse',
        conteudo=arquivoProcessadoComDuasAcoes,
        tipo_carga=CARGA_REPASSE_PREVISTO_SME,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_previsoes_repasses(arquivoCarga)
    assert arquivoCarga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_com_erro(arquivoCargaVirgula):
    carrega_previsoes_repasses(arquivoCargaVirgula)
    msg = """\nAssociação com código eol: 93238 não encontrado. Linha 1\nImportados 0 previsões de repasse. Erro na importação de 1 previsões."""
    assert arquivoCargaVirgula.log == msg
    assert arquivoCargaVirgula.status == ERRO


def test_carga_processado_com_erro(arquivoCargaVirgulaProcessado, periodo, associacao, conta_associacao, acao_associacao):
    assert not PrevisaoRepasseSme.objects.exists()
    carrega_previsoes_repasses(arquivoCargaVirgulaProcessado)
    msg = """\nAssociação com código eol: 93238 não encontrado. Linha 2\nImportados 1 previsões de repasse. Erro na importação de 1 previsões."""
    assert arquivoCargaVirgulaProcessado.log == msg
    assert arquivoCargaVirgulaProcessado.status == PROCESSADO_COM_ERRO
    assert PrevisaoRepasseSme.objects.exists()


def test_carga_processado_com_sucesso(arquivoCargaVirgulaProcessadoComDuasAcoes, periodo, associacao, conta_associacao, acao_associacao, acao_associacao_role_cultural):
    from decimal import Decimal
    assert not PrevisaoRepasseSme.objects.exists()
    carrega_previsoes_repasses(arquivoCargaVirgulaProcessadoComDuasAcoes)
    msg = """\nImportados 1 previsões de repasse. Erro na importação de 0 previsões."""
    assert arquivoCargaVirgulaProcessadoComDuasAcoes.log == msg
    assert arquivoCargaVirgulaProcessadoComDuasAcoes.status == SUCESSO
    assert len(PrevisaoRepasseSme.objects.all()) == 1
    assert PrevisaoRepasseSme.objects.first().valor_capital == Decimal("100000.98")
