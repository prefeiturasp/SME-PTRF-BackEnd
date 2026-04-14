import pytest
from openpyxl import Workbook
from sme_ptrf_apps.core.models import ArquivoDownload
from sme_ptrf_apps.core.fixtures.factories import ArquivoDownloadFactory
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download,
    atualiza_arquivo_download,
    atualiza_arquivo_download_erro,
)

pytestmark = pytest.mark.django_db


def test_gerar_arquivo_download():
    usr = UsuarioFactory.create()

    arquivo_download_gerado = gerar_arquivo_download(
        username=usr.username,
        identificador="teste",
        informacoes="info_teste"
    )

    arquivo_download_criado = ArquivoDownload.by_id(arquivo_download_gerado.id)

    assert arquivo_download_criado
    assert arquivo_download_criado.identificador == "teste"
    assert arquivo_download_criado.informacoes == "info_teste"
    assert arquivo_download_criado.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert arquivo_download_criado.dre is None  # Sem DRE especificada


def test_gerar_arquivo_download_com_dre():
    """Testa geração de arquivo download com DRE especificada"""
    from sme_ptrf_apps.core.fixtures.factories import UnidadeFactory

    usr = UsuarioFactory.create()
    dre = UnidadeFactory.create(tipo_unidade='DRE', codigo_eol='123456')

    arquivo_download_gerado = gerar_arquivo_download(
        username=usr.username,
        identificador="teste_com_dre",
        informacoes="info_teste_dre",
        dre_codigo_eol=dre.codigo_eol
    )

    arquivo_download_criado = ArquivoDownload.by_id(arquivo_download_gerado.id)

    assert arquivo_download_criado
    assert arquivo_download_criado.identificador == "teste_com_dre"
    assert arquivo_download_criado.informacoes == "info_teste_dre"
    assert arquivo_download_criado.status == ArquivoDownload.STATUS_EM_PROCESSAMENTO
    assert arquivo_download_criado.dre == dre


def test_atualiza_arquivo_download_com_workbook():
    obj = ArquivoDownloadFactory.create(status=ArquivoDownload.STATUS_EM_PROCESSAMENTO)
    wb = Workbook()
    wb.active.title = "Planilha"

    atualiza_arquivo_download(obj, wb)

    obj.refresh_from_db()
    assert obj.status == ArquivoDownload.STATUS_CONCLUIDO
    assert obj.arquivo


def test_atualiza_arquivo_download_com_field_file():
    obj_origem = ArquivoDownloadFactory.create()
    obj_destino = ArquivoDownloadFactory.create(status=ArquivoDownload.STATUS_EM_PROCESSAMENTO)

    field_file = obj_origem.arquivo  # FieldFile (pode ser vazio, mas o tipo é FieldFile)

    atualiza_arquivo_download(obj_destino, field_file)

    obj_destino.refresh_from_db()
    assert obj_destino.status == ArquivoDownload.STATUS_CONCLUIDO
    assert (obj_destino.arquivo.name or None) == (field_file.name or None)


def test_atualiza_arquivo_download_erro():
    obj = ArquivoDownloadFactory.create(status=ArquivoDownload.STATUS_EM_PROCESSAMENTO)

    atualiza_arquivo_download_erro(obj, "Erro ao processar arquivo")

    obj.refresh_from_db()
    assert obj.status == ArquivoDownload.STATUS_ERRO
    assert obj.msg_erro == "Erro ao processar arquivo"


def test_atualiza_arquivo_download_erro_com_excecao():
    obj = ArquivoDownloadFactory.create(status=ArquivoDownload.STATUS_EM_PROCESSAMENTO)

    try:
        raise ValueError("Falha inesperada")
    except ValueError as e:
        atualiza_arquivo_download_erro(obj, e)

    obj.refresh_from_db()
    assert obj.status == ArquivoDownload.STATUS_ERRO
    assert "Falha inesperada" in obj.msg_erro
