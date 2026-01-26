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


def test_criacao_conta_associacao_na_carga_repasses_previstos_com_valor_default(tipo_conta, associacao, periodo_2020_u):
    conta = get_conta_previstos(tipo_conta, associacao, periodo_2020_u)

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


@pytest.fixture
def periodo_2020_u(periodo_factory):
    return periodo_factory(
        referencia='2020.u',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 12, 31),
        periodo_anterior=None,
    )


def test_carga_com_erro(arquivo_carga_virgula, tipo_conta_cheque, periodo_2020_u):
    carrega_repasses_realizados(arquivo_carga_virgula)
    msg = """\nErro na linha 1: Associação com código eol: 93238 não encontrado. Linha ID:10
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


@pytest.fixture
def acao_role_cultural_teste():
    return baker.make('Acao', nome='Role Cultural')


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo, associacao, tipo_receita_repasse,
                                   tipo_conta_cheque, acao_role_cultural, acao_role_cultural_teste, periodo_2020_u):
    carrega_repasses_realizados(arquivo_carga_virgula_processado)
    msg = """\nErro na linha 1: Ação Rolê Cultural não permite capital.\nErro na linha 2: Associação com código eol: 93238 não encontrado. Linha ID:20
Foram criados 0 repasses. Erro na importação de 2 repasse(s)."""
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
    msg = """\nForam criados 1 repasses. Erro na importação de 0 repasse(s)."""
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
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""

    assert arquivo_carga_deve_criar_conta.log == msg
    assert arquivo_carga_deve_criar_conta.status == ERRO

def test_carga_em_conta_encerrada_deve_gerar_erro(periodos_de_2019_ate_2023, acao_factory, acao_associacao_factory, associacao_factory, arquivo_factory, unidade_factory, tipo_conta_factory, conta_associacao_factory, solicitacao_encerramento_conta_associacao_factory):
    from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao

    unidade = unidade_factory(codigo_eol='666666')
    associacao = associacao_factory(unidade=unidade)
    acao = acao_factory(nome='Acao teste', aceita_capital=True, aceita_custeio=True)
    acao_associacao_factory.create(associacao=associacao, acao=acao)
    tipo_conta = tipo_conta_factory.create(nome='Cheque')
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio='2018-10-20', tipo_conta=tipo_conta)
    solicitacao_encerramento_conta_associacao_factory.create(conta_associacao=conta, status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA)

    conteudo_arquivo = SimpleUploadedFile(f'carga_repasse_cheque.csv',
        bytes(f"""Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n10,666666,99000.98,99000.98,,Acao teste,02/04/2019,2019.2""", encoding="utf-8"))

    arquivo = arquivo_factory.create(identificador='carga_repasse_cheque', conteudo=conteudo_arquivo, tipo_carga=CARGA_REPASSE_REALIZADO, tipo_delimitador=DELIMITADOR_VIRGULA)

    carrega_repasses_realizados(arquivo)

    msg= """\nErro na linha 1: A conta possui pedido de encerramento aprovado pela DRE.\nForam criados 0 repasses. Erro na importação de 1 repasse(s)."""

    assert arquivo.log == msg
    assert arquivo.status == ERRO


@pytest.fixture
def arquivo_associacao_periodo_com_pc():
    return SimpleUploadedFile(
        f'carga_repasse_cheque_2.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao,Data receita,Periodo\n10,123456,99000.98,99000.98,,PTRF Básico,01/01/2024,2024.1""",
            encoding="utf-8"))


@pytest.fixture
def arquivo_carga_associacao_periodo_com_pc(arquivo_associacao_periodo_com_pc):
    return baker.make(
        'Arquivo',
        identificador='2024_01_01_a_2024_06_30_cheque_2',
        conteudo=arquivo_associacao_periodo_com_pc,
        tipo_carga=CARGA_REPASSE_REALIZADO,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def periodo_pc(periodo_factory):
    return periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=datetime.date(2024, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2024, 6, 30),
    )


@pytest.fixture
def pc_teste(periodo_pc, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_pc,
        associacao=associacao,
        data_recebimento=datetime.date(2024, 1, 1),
        status='DEVOLVIDA'
    )


def test_carga_processado_com_erro_associacao_periodo_com_pc(
    arquivo_carga_associacao_periodo_com_pc,
    associacao,
    pc_teste,
    tipo_receita_repasse,
    tipo_conta_cheque,
    acao_ptrf_basico
):
    carrega_repasses_realizados(arquivo_carga_associacao_periodo_com_pc)
    msg = "Erro ao processar repasses realizados: Não foi possível realizar a carga. Já existem PCs geradas no período."
    assert arquivo_carga_associacao_periodo_com_pc.log == msg
    assert arquivo_carga_associacao_periodo_com_pc.status == ERRO
