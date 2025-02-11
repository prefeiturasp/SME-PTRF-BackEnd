import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker

from sme_ptrf_apps.core.services.carga_contas_associacoes_service import CargaContasAssociacoesService
from ...models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    PROCESSADO_COM_ERRO,
    SUCESSO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_CONTAS_ASSOCIACOES

pytestmark = pytest.mark.django_db


CSV_CABECALHO_INCORRETO = bytes(
    """Código de unidade;Tipo de conta;Status;Nome do banco;Nº da agência;Nº da conta;Data de início da conta
    123456;Cartão;Ativa;Banco do Brasil;1897-X;19.150-7;01/06/2024""", encoding="utf-8")


CSV_DELIMITADOR_INVALIDO = bytes(
    """Código de unidade|Tipo de conta|Status|Nome do banco|Nº da agência|Nº da conta|Data de início da conta""",
    encoding="utf-8")


CSV_LOTE_CONTAS = bytes(
    """Código eol;Tipo de conta;Status;Nome do banco;Nº da agência;Nº da conta;Data de início da conta
    123456;Cartão;Ativa;Banco do Brasil;1897-X;19.150-7;01/06/2024
    123456;Cartão;Ativa;Banco do Brasil 2;1898-X;19.151-7;01/07/2024
    123456;Cartão;Inativa;C6 bank;1898-X;19.151-7;02/06/2024
    123456;Débito;Ativa;Nu Bank;1899;191527;03/06/2024""", encoding="utf-8")


CSV_LOTE_COM_ERRO = bytes(
    """Código eol;Tipo de conta;Status;Nome do banco;Nº da agência;Nº da conta;Data de início da conta
    123456;Cartão;Ativa;Banco do Brasil;1897-X;19.150-7;01/06/2024
    123456;;Inativa;C6 bank;1898-X;19.151-7;02/06/2024
    123456;Cartão;BLOQUEADO;C6 bank;1898-X;19.151-7;02/06/2024
    123456;Cartão;Inativa;C6 bank;1898-X;19.151-7;
    123456;Cartão;Inativa;C6 bank;1898-X;19.151-7;01/15/2024
    999090;;Inativa;C6 bank;1898-X;19.151-7;02/06/2024
    ;;Inativa;C6 bank;1898-X;19.151-7;02/06/2024
    123456;Cartão;;C6 bank;1898-X;19.151-7;02/06/2024
    123456;TipoContaInexistente;Ativa;Nu Bank;1899;191527;03/06/2024""", encoding="utf-8")


@pytest.fixture
def arquivo_cabecalho_incorreto():
    return SimpleUploadedFile('arquivo.csv', CSV_CABECALHO_INCORRETO)


@pytest.fixture
def arquivo_delimitador_invalido():
    return SimpleUploadedFile('arquivo.csv', CSV_DELIMITADOR_INVALIDO)


@pytest.fixture
def arquivo():
    return SimpleUploadedFile('arquivo.csv', CSV_LOTE_CONTAS)


@pytest.fixture
def arquivo_com_erro():
    return SimpleUploadedFile('arquivo.csv', CSV_LOTE_COM_ERRO)


@pytest.fixture
def tipo_conta_cartao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def tipo_conta_debito():
    return baker.make('TipoConta', nome='Débito')


@pytest.fixture
def unidade(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre)


@pytest.fixture
def associacao(periodo_2019_2, periodo_2020_2, unidade):
    return baker.make(
        'Associacao',
        nome='Associacao Teste',
        cnpj='01.234.567/0008-90',
        unidade=unidade,
        periodo_inicial=periodo_2019_2,
        data_de_encerramento=periodo_2020_2.data_fim_realizacao_despesas)


@pytest.fixture
def arquivo_carga_virgula(arquivo):
    # Arquivo com delimitador diferente do esperado
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_VIRGULA)


@pytest.fixture
def arquivo_carga_delimitador_invalido(arquivo_delimitador_invalido):
    # Arquivo com delimitador diferente do esperado
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo_delimitador_invalido,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA)


@pytest.fixture
def arquivo_carga_ponto_e_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA)


@pytest.fixture
def arquivo_carga_com_erro(arquivo_com_erro):
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo_com_erro,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA)


@pytest.fixture
def arquivo_carga_cabecalho_incorreto(arquivo_cabecalho_incorreto):
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo_cabecalho_incorreto,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA)


@pytest.fixture
def arquivo_carga_ponto_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_contas_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_CONTAS_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga_virgula):
    CargaContasAssociacoesService().carrega_contas_associacoes(arquivo_carga_virgula)
    msg = ("""\nLinha:0 Formato definido (DELIMITADOR_VIRGULA) é diferente do formato """ +
           """do arquivo csv (DELIMITADOR_PONTO_VIRGULA)\n0 linha(s) importada(s) com """ +
           """sucesso. 1 erro(s) reportado(s).""")
    assert arquivo_carga_virgula.log == msg
    assert arquivo_carga_virgula.status == ERRO


def test_carga_contas(arquivo_carga_ponto_e_virgula, associacao, tipo_conta_cartao, tipo_conta_debito):
    CargaContasAssociacoesService().carrega_contas_associacoes(arquivo_carga_ponto_e_virgula)
    msg = "linha(s) importada(s) com sucesso. 0 erro(s) reportado(s)."
    assert msg in arquivo_carga_ponto_e_virgula.log
    assert arquivo_carga_ponto_e_virgula.status == SUCESSO


def test_carga_contas_cabecalho_incorreto(arquivo_carga_cabecalho_incorreto, associacao, tipo_conta_cartao):
    CargaContasAssociacoesService().carrega_contas_associacoes(arquivo_carga_cabecalho_incorreto)
    msg = "Encontrado \"Código de unidade\". Deveria ser \"Código eol\". Confira o arquivo com o modelo."
    assert msg in arquivo_carga_cabecalho_incorreto.log
    assert arquivo_carga_cabecalho_incorreto.status == ERRO


def test_carga_contas_delimitador_invalido(arquivo_carga_delimitador_invalido):
    CargaContasAssociacoesService().carrega_contas_associacoes(arquivo_carga_delimitador_invalido)
    msg = "Erro ao processar contas de associações"
    assert msg in arquivo_carga_delimitador_invalido.log
    assert arquivo_carga_delimitador_invalido.status == ERRO


def test_carga_contas_processado_com_erro(arquivo_carga_com_erro, associacao, tipo_conta_cartao):
    CargaContasAssociacoesService().carrega_contas_associacoes(arquivo_carga_com_erro)
    msg_tipo_conta_nao_existe = "Tipo de conta None não existe."
    msg_tipo_conta_nao_informado = "Tipo de conta não informado."
    msg_codigo_eol_inexistente = "Código EOL não existe: 999090"
    msg_codigo_eol_nao_informado = "Código EOL não informado."
    msg_status_invalido = "Status inválido"
    msg_status_nao_informado = "Status de conta não informado."
    msg_data_nao_informada = "Data de início não informada."
    msg_data_invalida = "Data informada fora do padrão"
    assert msg_tipo_conta_nao_existe in arquivo_carga_com_erro.log
    assert msg_tipo_conta_nao_informado in arquivo_carga_com_erro.log
    assert msg_codigo_eol_inexistente in arquivo_carga_com_erro.log
    assert msg_codigo_eol_nao_informado in arquivo_carga_com_erro.log
    assert msg_status_nao_informado in arquivo_carga_com_erro.log
    assert msg_status_invalido in arquivo_carga_com_erro.log
    assert msg_data_nao_informada in arquivo_carga_com_erro.log
    assert msg_data_invalida in arquivo_carga_com_erro.log
    assert arquivo_carga_com_erro.status == PROCESSADO_COM_ERRO
