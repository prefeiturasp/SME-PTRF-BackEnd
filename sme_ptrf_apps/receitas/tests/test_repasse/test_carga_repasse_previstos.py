import pytest
import datetime

from sme_ptrf_apps.core.models import ContaAssociacao
from sme_ptrf_apps.receitas.services.carga_repasses_previstos import carrega_repasses_previstos
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from sme_ptrf_apps.core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    SUCESSO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_REPASSE_PREVISTO

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'2020_01_01_a_2020_06_30_cheque.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,93238,99000.98,99000.98,,Role Cultural""",
            encoding="utf-8"))


@pytest.fixture
def arquivo_deve_criar_conta():
    return SimpleUploadedFile(
        f'2023_01_01_a_2023_06_30_cartao.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,123456,99000.98,99000.98,,PTRF Básico""",
            encoding="utf-8"))


@pytest.fixture
def arquivo_processado():
    return SimpleUploadedFile(
        f'carga_repasse_cheque.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,123456,99000.98,99000.98,,Role Cultural\n20,93238,99000.98,99000.98,,Role Cultural""",
            encoding="utf-8"))


@pytest.fixture
def arquivo_associacao_encerrada():
    return SimpleUploadedFile(
        f'carga_repasse_cheque_2.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,999999,99000.98,99000.98,,PTRF Básico""",
            encoding="utf-8"))


@pytest.fixture
def periodo_teste_2(periodo_factory):
    return periodo_factory(
        referencia='2020.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2020, 6, 30),
    )


@pytest.fixture
def tipo_conta(tipo_conta_factory):
    return tipo_conta_factory(
        nome='Cheque',
        banco_nome='Banco do Inter',
        agencia='67945',
        numero_conta='935556-x',
        numero_cartao='987644164221'
    )


@pytest.fixture
def arquivo_carga(arquivo, tipo_conta, periodo_teste_2):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_teste_2
    )


@pytest.fixture
def periodo_2024(periodo_factory):
    return periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=datetime.date(2024, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2024, 8, 31),
    )


@pytest.fixture
def periodo_teste_2(periodo_factory):
    return periodo_factory(
        referencia='2023.1',
        data_inicio_realizacao_despesas=datetime.date(2023, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 6, 30),
    )


@pytest.fixture
def arquivo_carga_cartao_deve_criar_conta(arquivo_deve_criar_conta, tipo_conta, periodo_teste_2):
    return baker.make(
        'Arquivo',
        identificador='2023_01_01_a_2023_06_30_cartao',
        conteudo=arquivo_deve_criar_conta,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_teste_2
    )


@pytest.fixture
def periodo_teste_4(periodo_factory):
    return periodo_factory(
        referencia='2023.1',
        data_inicio_realizacao_despesas=datetime.date(2020, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2023, 6, 30),
    )


@pytest.fixture
def arquivo_carga_virgula(arquivo, tipo_conta, periodo_teste_4):
    return baker.make(
        'Arquivo',
        identificador='2020_01_01_a_2020_06_30_cheque',
        conteudo=arquivo,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_4,
        tipo_de_conta=tipo_conta,
    )


@pytest.fixture
def periodo_teste_5(periodo_factory):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def arquivo_carga_virgula_processado(arquivo_processado, periodo_teste_5, tipo_conta):
    return baker.make(
        'Arquivo',
        identificador='2019_01_01_a_2019_11_30_cheque',
        conteudo=arquivo_processado,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_5,
        tipo_de_conta=tipo_conta,
    )


@pytest.fixture
def periodo_teste_1(periodo_factory):
    return periodo_factory(
        referencia='2029.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def arquivo_carga_virgula_processado_com_associacao_encerrada(arquivo_associacao_encerrada, periodo_teste_1, tipo_conta):
    return baker.make(
        'Arquivo',
        identificador='2019_01_01_a_2019_11_30_cheque_2',
        conteudo=arquivo_associacao_encerrada,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        periodo=periodo_teste_1,
        tipo_de_conta=tipo_conta
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
def acao_role_cultural_teste(acao_factory):
    return acao_factory(nome='Role Cultural')


@pytest.fixture
def acao_ptrf_basico(acao_factory):
    return acao_factory(nome='PTRF Básico',
                        aceita_capital=True, aceita_custeio=True,
                        aceita_livre=True)


@pytest.fixture
def conta_associacao_cartao_teste_data_inicio(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        data_inicio=datetime.date(2024, 1, 1)
    )


def test_carga_processado_com_erro(arquivo_carga_virgula_processado, periodo_teste_1, associacao, tipo_receita_repasse,
                                   tipo_conta_cheque, acao_role_cultural, acao_role_cultural_teste):
    carrega_repasses_previstos(arquivo_carga_virgula_processado)
    msg = """Erro na linha 1: Ação Role Cultural não permite capital.\nErro na linha 2: Associação com código eol: 93238 não encontrado.
Foram criados 0 repasses. Erro na importação de 2 repasse(s)."""
    assert arquivo_carga_virgula_processado.log == msg
    assert arquivo_carga_virgula_processado.status == ERRO


def test_carga_processado_com_erro_associacao_encerrada(arquivo_carga_virgula_processado_com_associacao_encerrada,
                                                        associacao_encerrada_2020_2,
                                                        periodo, tipo_receita_repasse, tipo_conta_cheque,
                                                        acao_ptrf_basico):
    carrega_repasses_previstos(arquivo_carga_virgula_processado_com_associacao_encerrada)
    msg = """Erro na linha 1: A associação foi encerrada em 31/12/2020. Linha ID:1
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_virgula_processado_com_associacao_encerrada.log == msg
    assert arquivo_carga_virgula_processado_com_associacao_encerrada.status == ERRO


def test_carga_deve_criar_conta(
    arquivo_carga_cartao_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta_cartao,
    acao_ptrf_basico,
    tipo_conta
):
    assert not ContaAssociacao.objects.filter(tipo_conta=tipo_conta_cartao, associacao=associacao).exists()
    carrega_repasses_previstos(arquivo_carga_cartao_deve_criar_conta)
    msg = """Foram criados 1 repasses. Erro na importação de 0 repasse(s)."""
    assert arquivo_carga_cartao_deve_criar_conta.log == msg
    assert arquivo_carga_cartao_deve_criar_conta.status == SUCESSO
    conta_associacao_cartao = ContaAssociacao.objects.get(tipo_conta=tipo_conta, associacao=associacao)
    assert conta_associacao_cartao.data_inicio == datetime.date(2023, 1, 1)


def test_carga_deve_gerar_erro_periodo_anterior_a_criacao_da_conta(
    arquivo_carga_cartao_deve_criar_conta,
    associacao,
    periodo,
    tipo_receita_repasse,
    tipo_conta,
    conta_associacao_cartao_teste_data_inicio,
    acao_ptrf_basico
):
    carrega_repasses_previstos(arquivo_carga_cartao_deve_criar_conta)
    msg = """Erro na linha 1: O período informado de repasse é anterior ao período de criação da conta.
Foram criados 0 repasses. Erro na importação de 1 repasse(s)."""
    assert arquivo_carga_cartao_deve_criar_conta.log == msg
    assert arquivo_carga_cartao_deve_criar_conta.status == ERRO


def test_carga_em_conta_encerrada_deve_gerar_erro(periodos_de_2019_ate_2023, acao_factory, acao_associacao_factory, associacao_factory, arquivo_factory, unidade_factory, tipo_conta_factory, conta_associacao_factory, solicitacao_encerramento_conta_associacao_factory, periodo_factory):
    from sme_ptrf_apps.core.models.solicitacao_encerramento_conta_associacao import SolicitacaoEncerramentoContaAssociacao

    unidade = unidade_factory(codigo_eol='666666')
    associacao = associacao_factory(unidade=unidade)
    acao = acao_factory(nome='Acao teste', aceita_capital=True, aceita_custeio=True)
    acao_associacao_factory.create(associacao=associacao, acao=acao)
    tipo_conta = tipo_conta_factory.create(nome='Cheque')
    conta = conta_associacao_factory.create(associacao=associacao, data_inicio='2018-10-20', tipo_conta=tipo_conta)
    solicitacao_encerramento_conta_associacao_factory.create(
        conta_associacao=conta, status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA)
    periodo = periodo_factory.create(data_inicio_realizacao_despesas=datetime.date(
        2023, 1, 1), data_fim_realizacao_despesas=datetime.date(2023, 5, 30))

    conteudo_arquivo = SimpleUploadedFile(f'2020_01_01_a_2020_06_30_cheque.csv',
                                          bytes(f"""Linha_ID,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,666666,200,200,,Acao teste""", encoding="utf-8"))

    arquivo = arquivo_factory.create(identificador='2020_01_01_a_2020_06_30_cheque', conteudo=conteudo_arquivo,
                                     tipo_carga=CARGA_REPASSE_PREVISTO, tipo_delimitador=DELIMITADOR_VIRGULA, tipo_de_conta=tipo_conta, periodo=periodo)

    carrega_repasses_previstos(arquivo)

    msg = """Erro na linha 1: A conta possui pedido de encerramento aprovado pela DRE.\nForam criados 0 repasses. Erro na importação de 1 repasse(s)."""

    assert arquivo.log == msg
    assert arquivo.status == ERRO


@pytest.fixture
def arquivo_associacao_periodo_com_pc():
    return SimpleUploadedFile(
        f'carga_repasse_cheque_2.csv',
        bytes(
            f"""Id_Linha,Código eol,Valor capital,Valor custeio,Valor livre aplicacao,Acao\n10,123456,99000.98,99000.98,,PTRF Básico""",
            encoding="utf-8"))


@pytest.fixture
def arquivo_carga_associacao_periodo_com_pc(arquivo_associacao_periodo_com_pc, tipo_conta, periodo_2024):
    return baker.make(
        'Arquivo',
        identificador='cheque_2',
        conteudo=arquivo_associacao_periodo_com_pc,
        tipo_carga=CARGA_REPASSE_PREVISTO,
        tipo_delimitador=DELIMITADOR_VIRGULA,
        tipo_de_conta=tipo_conta,
        periodo=periodo_2024
    )


@pytest.fixture
def periodo_pc(periodo_factory):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=datetime.date(2019, 1, 1),
        data_fim_realizacao_despesas=datetime.date(2019, 11, 30),
    )


@pytest.fixture
def pc_teste(periodo_2024, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2024,
        associacao=associacao,
        data_recebimento=datetime.date(2020, 1, 1),
        status='APROVADA'
    )


def test_carga_processado_com_erro_associacao_periodo_com_pc(
    arquivo_carga_associacao_periodo_com_pc,
    periodo_pc,
    associacao,
    pc_teste,
    tipo_receita_repasse,
    tipo_conta_cheque,
    acao_ptrf_basico
):
    carrega_repasses_previstos(arquivo_carga_associacao_periodo_com_pc)
    msg = "Erro ao processar repasses previstos: Já existe prestações de conta para o período 2024.1."
    assert arquivo_carga_associacao_periodo_com_pc.log == msg
    assert arquivo_carga_associacao_periodo_com_pc.status == ERRO
