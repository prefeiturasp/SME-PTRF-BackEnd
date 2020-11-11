import pytest
import datetime

from sme_ptrf_apps.receitas.services.carga_repasses_realizados import get_conta_associacao as get_conta_realizado
from sme_ptrf_apps.receitas.services.carga_repasses_previstos import get_conta_associacao as get_conta_previstos
from sme_ptrf_apps.receitas.services.carga_repasses_realizados import carrega_repasses_realizados
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.models.arquivo import (
    CARGA_REPASSE_REALIZADO,
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO)

pytestmark = pytest.mark.django_db


def test_criacao_conta_associacao_na_carga_repasses_realizados_com_valor_default(tipo_conta, associacao):
    conta = get_conta_realizado(tipo_conta, associacao)

    assert conta.banco_nome == "Banco do Inter"
    assert conta.agencia == '67945'
    assert conta.numero_conta == '935556-x'
    assert conta.numero_cartao == '987644164221'


def test_criacao_conta_associacao_na_carga_repasses_previstos_com_valor_default(tipo_conta, associacao):
    conta = get_conta_previstos(tipo_conta, associacao)

    assert conta.banco_nome == "Banco do Inter"
    assert conta.agencia == '67945'
    assert conta.numero_conta == '935556-x'
    assert conta.numero_cartao == '987644164221'


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
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
        identificador='carga_repasse_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )

@pytest.fixture
def arquivoCargaVirgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivoCargaVirgulaProcessado(arquivoProcessado):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cheque',
        conteudo=arquivoProcessado,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivoCarga):
    carrega_repasses_realizados(arquivoCarga)
    assert arquivoCarga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivoCarga.status == ERRO


def test_carga_com_erro(arquivoCargaVirgula):
    carrega_repasses_realizados(arquivoCargaVirgula)
    msg = """\nAssociação com código eol: 93238 não encontrado. Linha 1
Foram criados 0 repasses. Erro na importação de 1 repasses."""
    assert arquivoCargaVirgula.log == msg
    assert arquivoCargaVirgula.status == ERRO


def test_carga_processado_com_erro(arquivoCargaVirgulaProcessado, periodo, associacao, tipo_receita_repasse):
    carrega_repasses_realizados(arquivoCargaVirgulaProcessado)
    msg = """\nAssociação com código eol: 93238 não encontrado. Linha 2
Foram criados 1 repasses. Erro na importação de 1 repasses."""
    assert arquivoCargaVirgulaProcessado.log == msg
    assert arquivoCargaVirgulaProcessado.status == PROCESSADO_COM_ERRO
