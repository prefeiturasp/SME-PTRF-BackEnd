import pytest
from sme_ptrf_apps.core.models import ArquivoDownload
from sme_ptrf_apps.users.fixtures.factories import UsuarioFactory
from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download

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

