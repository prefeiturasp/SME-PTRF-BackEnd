import pytest

from unittest.mock import patch, call

from django.core.files.uploadedfile import SimpleUploadedFile

from model_bakery import baker

from sme_ptrf_apps.core.services.carga_acoes_associacoes_service import CargaAcoesAssociacoesService, CargaAcoesAssociacaoException

from ...models import AcaoAssociacao
from ...models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    ERRO,
    SUCESSO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.core.choices.tipos_carga import CARGA_ACOES_ASSOCIACOES

pytestmark = pytest.mark.django_db


@pytest.fixture
def arquivo():
    return SimpleUploadedFile(
        f'arquivo.csv',
        bytes(f"""Código EOL;Ação;Status
000086;PTRF Básico;Ativa
000094;PTRF Básico;Inativa
000108;PTRF Básico;Ativa""", encoding="utf-8"))


@pytest.fixture
def arquivo_carga(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_acoes_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_ACOES_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_VIRGULA
    )


@pytest.fixture
def arquivo_carga_ponto_virgula(arquivo):
    return baker.make(
        'Arquivo',
        identificador='carga_acoes_associacoes',
        conteudo=arquivo,
        tipo_carga=CARGA_ACOES_ASSOCIACOES,
        tipo_delimitador=DELIMITADOR_PONTO_VIRGULA
    )


def test_carga_com_erro_formatacao(arquivo_carga):
    CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo_carga)
    msg = """\nLinha:0 Formato definido (DELIMITADOR_VIRGULA) é diferente do formato do arquivo csv (DELIMITADOR_PONTO_VIRGULA)\n0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    assert arquivo_carga.log == msg
    assert arquivo_carga.status == ERRO

def test_carrega_e_valida_dados_acao_associacao():
    linha_conteudo = ["000086", "PTRF Básico", "Ativa"]
    linha_index = 1

    
    dados = CargaAcoesAssociacoesService().carrega_e_valida_dados_acao_associacao(linha_conteudo, linha_index)
    assert dados["eol_unidade"] == "000086"
    assert dados["acao"] == "PTRF Básico"
    assert dados["status"] == "Ativa"

def test_verifica_estrutura_cabecalho_success():
    cabecalho = ["Código EOL", "Ação", "Status"]
    retorno = CargaAcoesAssociacoesService().verifica_estrutura_cabecalho(cabecalho)
    assert retorno is True


def test_verifica_estrutura_cabecalho_error():
    cabecalho = ["Código", "Ação", "Status"]
    
    with pytest.raises(CargaAcoesAssociacaoException) as e:
        CargaAcoesAssociacoesService().verifica_estrutura_cabecalho(cabecalho)
    
    assert str(e.value) == 'Título da coluna 0 errado. Encontrado "Código". Deveria ser "Código EOL". Confira o arquivo com o modelo.'


def test_cria_ou_atualiza_acao_associacao_criacao(associacao_factory, acao_factory):
    associacao = associacao_factory.create()
    acao = acao_factory.create()
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "associacao_obj": associacao,
        "acao_obj": acao,
        "status": "ATIVA"
    }
    retorno = service.cria_ou_atualiza_acao_associacao()
    assert isinstance(retorno, AcaoAssociacao)
    assert retorno.associacao == associacao
    assert retorno.acao == acao


def test_cria_ou_atualiza_acao_associacao_edicao(acao_associacao_factory, associacao_factory, acao_factory):
    associacao = associacao_factory.create()
    acao = acao_factory.create()
    acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=acao, status="INATIVA")
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "associacao_obj": associacao,
        "acao_obj": acao,
        "status": "ATIVA"
    }
    retorno = service.cria_ou_atualiza_acao_associacao()
    assert isinstance(retorno, AcaoAssociacao)
    assert retorno.associacao == associacao
    assert retorno.acao == acao
    assert retorno.status == "ATIVA"


def test_cria_ou_atualiza_acao_associacao_edicao_duplicado(acao_associacao_factory, associacao_factory, acao_factory):
    associacao = associacao_factory.create()
    acao = acao_factory.create()
    acao_associacao = acao_associacao_factory.create(associacao=associacao, acao=acao, status="INATIVA")
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "associacao_obj": associacao,
        "acao_obj": acao,
        "status": "INATIVA"
    }
    with pytest.raises(CargaAcoesAssociacaoException) as e:
        service.cria_ou_atualiza_acao_associacao()
    
    assert str(e.value) == "A ação já foi criada para a unidade educacional"


def test_valida_codigo_eol_e_associacao_success(associacao_factory, unidade_factory):
    unidade = unidade_factory.create(codigo_eol="007007")
    associacao = associacao_factory.create(unidade=unidade)
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "eol_unidade": "007007",
        "associacao_obj": None,
    }
    service.valida_codigo_eol_e_associacao()
    assert service._CargaAcoesAssociacoesService__dados_acao_associacao["associacao_obj"] == associacao


def test_valida_codigo_eol_e_associacao_error(associacao_factory, unidade_factory):
    unidade = unidade_factory.create(codigo_eol="007007")
    associacao = associacao_factory.create(unidade=unidade)
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "eol_unidade": "007008",
        "associacao_obj": None,
    }
    with pytest.raises(CargaAcoesAssociacaoException) as e:
        service.valida_codigo_eol_e_associacao()
    assert str(e.value) == "Código EOL não existe"


def test_valida_acao_success(acao_factory):
    acao = acao_factory.create(nome="Ação 007")
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "acao": "Ação 007",
        "acao_obj": None,
    }
    service.valida_acao()
    assert service._CargaAcoesAssociacoesService__dados_acao_associacao["acao_obj"] == acao


def test_valida_valida_acao_error(acao_factory):
    acao = acao_factory.create(nome="Ação 007")
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "acao": "Ação 006",
        "acao_obj": None,
    }
    with pytest.raises(CargaAcoesAssociacaoException) as e:
        service.valida_acao()
    assert str(e.value) == "Ação não existe"


def test_valida_status_succes():
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "status": "ATIVA"
    }
    assert service._CargaAcoesAssociacoesService__dados_acao_associacao["status"] == "ATIVA"


def test_valida_status_error():
    service = CargaAcoesAssociacoesService()
    service._CargaAcoesAssociacoesService__dados_acao_associacao = {
        "status": "AATIVA"
    }
    with pytest.raises(CargaAcoesAssociacaoException) as e:
        service.valida_status()
    assert str(e.value) == "Status AATIVA inválido"

def test_carrega_acoes_associacoes_error_delimitador_virgula(arquivo_carga):
    CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo_carga)
    msg = f"""\nLinha:0 Formato definido ({DELIMITADOR_VIRGULA}) é diferente do formato do arquivo csv ({DELIMITADOR_PONTO_VIRGULA})
0 linha(s) importada(s) com sucesso. 1 erro(s) reportado(s)."""
    
    assert arquivo_carga.log == msg
    assert arquivo_carga.status == ERRO


def test_carrega_acoes_associacoes_success_delimitador_ponto_virgula(
        arquivo_carga_ponto_virgula,
        associacao_factory,
        unidade_factory,
        acao_factory
    ):
    acao_factory.create(nome="PTRF Básico")
    unidade_1 = unidade_factory.create(codigo_eol="000086")
    unidade_2 = unidade_factory.create(codigo_eol="000094")
    unidade_3 = unidade_factory.create(codigo_eol="000108")
    associacao_factory.create(unidade=unidade_1)
    associacao_factory.create(unidade=unidade_2)
    associacao_factory.create(unidade=unidade_3)
    CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo_carga_ponto_virgula)
    msg = f"""\n3 linha(s) importada(s) com sucesso. 0 erro(s) reportado(s)."""
    
    assert arquivo_carga_ponto_virgula.log == msg
    assert arquivo_carga_ponto_virgula.status == SUCESSO


@patch.object(CargaAcoesAssociacoesService, "verifica_estrutura_cabecalho")
@patch.object(CargaAcoesAssociacoesService, "atualiza_status_arquivo")
def test_carrega_acoes_associacoes_error(
    mock_atualiza_status_arquivo,
    mock_verifica_estrutura_cabecalho, 
    arquivo_carga_ponto_virgula
):
    mock_verifica_estrutura_cabecalho.side_effect = CargaAcoesAssociacaoException("Erro 123")
    mock_atualiza_status_arquivo.side_effect = Exception("Erro 321")

    with pytest.raises(Exception) as e:
        CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo_carga_ponto_virgula)
    
    assert str(e.value) == "Erro 321"


@patch.object(CargaAcoesAssociacoesService, "carrega_e_valida_dados_acao_associacao")
def test_carrega_acoes_associacoes_error_002(
    mock_carrega_e_valida_dados_acao_associacao, 
    arquivo_carga_ponto_virgula
):
    mock_carrega_e_valida_dados_acao_associacao.side_effect = [CargaAcoesAssociacaoException("Erro 123")] * 3

    CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo_carga_ponto_virgula)
    assert arquivo_carga_ponto_virgula.status == ERRO

    erro = """\nLinha:1 Houve um erro na carga dessa linha: Erro 123\nLinha:2 Houve um erro na carga dessa linha: Erro 123\nLinha:3 Houve um erro na carga dessa linha: Erro 123\n0 linha(s) importada(s) com sucesso. 3 erro(s) reportado(s)."""
    assert arquivo_carga_ponto_virgula.log == erro
