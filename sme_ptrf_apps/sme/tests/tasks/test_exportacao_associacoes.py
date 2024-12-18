import pytest

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.sme.tasks.exportar_associacoes import exportar_associacoes_async


pytestmark = pytest.mark.django_db


def test_exportacoes_associacoes_async(associacoes, data_inicio, data_final, usuario):
    exportar_associacoes_async(
        data_inicio=data_inicio,
        data_final=data_final,
        username=usuario.username
    )

    assert ArquivoDownload.objects.count() == 1


def test_exportacoes_associacoes_async_com_dre(associacoes, data_inicio, data_final, usuario):
    dre_uuid = Associacao.objects.first().unidade.dre.uuid

    exportar_associacoes_async(
        data_inicio=data_inicio,
        data_final=data_final,
        username=usuario.username,
        dre_uuid=str(dre_uuid)
    )

    assert ArquivoDownload.objects.count() == 1
