import pytest
import datetime

from sme_ptrf_apps.core.models import ContaAssociacao
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
    SUCESSO)

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
def arquivo_deve_criar_conta():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
        bytes(f"""Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n10,123456,99000.98,99000.98,,PTRF Básico,06/06/2019,2019.2""", encoding="utf-8"))


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
        bytes(f"""Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n10,93238,99000.98,99000.98,,Rolê Cultural,02/01/2020,2020.u""", encoding="utf-8"))


@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
        bytes(f"""Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n10,123456,99000.98,99000.98,,Rolê Cultural,02/04/2019,2019.2\n20,93238,99000.98,99000.98,,Role Cultural,02/01/2020,2020.u""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga_deve_criar_conta(arquivo_deve_criar_conta):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cartao',
        conteudo=arquivo_deve_criar_conta,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )



@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado):
    return baker.make(
        'Arquivo',
        identificador='carga_repasse_cheque',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def conta_associacao_cartao_teste_data_inicio(associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cartao,
        data_inicio=datetime.date(2024, 1, 1)
    )

@pytest.fixture
def acao_ptrf_basico():
    return baker.make('Acao', nome='PTRF Básico',
                      aceita_capital=True, aceita_custeio=True,
                      aceita_livre=True)


def test_carga_com_erro_formatacao(arquivo_carga, tipo_conta_cheque):
    carrega_repasses_realizados(arquivo_carga)
    assert arquivo_carga.log == 'Formato definido (DELIMITADOR_PONTO_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_VIRGULA)'
    assert arquivo_carga.status == ERRO


def test_carga_com_erro(arquivo_carga_virgula, tipo_conta_cheque):
    carrega_repasses_realizados(arquivo_carga_virgula)
    msg = """\nErro na linha 1: Associação com código eol: 93238 não encontrado. Linha ID:10
Foram criados 0 repasses. Erro na importação de 1 repasses."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


@pytest.fixture
def acao_role_cultural_teste():
    return baker.make('Acao', nome='Role Cultural')


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo, associacao, tipo_receita_repasse,
                                   tipo_conta_cheque, acao_role_cultural, acao_role_cultural_teste):
    carrega_repasses_realizados(arquivo_carga_virgula_processado)
    msg = """\nErro na linha 1: Ação Rolê Cultural não permite capital.\nErro na linha 2: Associação com código eol: 93238 não encontrado. Linha ID:20
Foram criados 0 repasses. Erro na importação de 2 repasses."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == ERRO


def test_carga_deve_criar_conta(
    arquivo_carga_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta_cartao,
    acao_ptrf_basico,
):
    assert not ContaAssociacao.objects.filter(tipo_conta=tipo_conta_cartao, associacao=associacao).exists()
    carrega_repasses_realizados(arquivo_carga_deve_criar_conta)
    msg = """\nForam criados 1 repasses. Erro na importação de 0 repasses."""
    assert arquivo_carga_deve_criar_conta.log == msg
    assert arquivo_carga_deve_criar_conta.status == SUCESSO
    conta_associacao_cartao = ContaAssociacao.objects.get(tipo_conta=tipo_conta_cartao, associacao=associacao)
    assert conta_associacao_cartao.data_inicio == datetime.date(2019, 9, 1)


def test_carga_deve_gerar_erro_periodo_anterior_a_criacao_da_conta(
    arquivo_carga_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta_cartao,
    acao_ptrf_basico,
    conta_associacao_cartao_teste_data_inicio
):
    carrega_repasses_realizados(arquivo_carga_deve_criar_conta)

    msg= """\nErro na linha 1: O período informado de repasse é anterior ao período de criação da conta.
Foram criados 0 repasses. Erro na importação de 1 repasses."""

    assert arquivo_carga_deve_criar_conta.log == msg
    assert arquivo_carga_deve_criar_conta.status == ERRO
