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

