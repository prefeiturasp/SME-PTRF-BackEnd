import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import MembroComissao, PresenteAtaDre

pytestmark = pytest.mark.django_db


def test_delete_membro_comissao(
    jwt_authenticated_client_dre,
    membro_alex_comissao_a_dre_x,
    presente_ata_dre,
):
    assert MembroComissao.objects.filter(uuid=membro_alex_comissao_a_dre_x.uuid).exists()
    assert PresenteAtaDre.objects.filter(id=presente_ata_dre.id).exists()

    response = jwt_authenticated_client_dre.delete(
        f"/api/membros-comissoes/{membro_alex_comissao_a_dre_x.uuid}/",
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not MembroComissao.objects.filter(uuid=membro_alex_comissao_a_dre_x.uuid).exists()

    assert not PresenteAtaDre.objects.filter(id=presente_ata_dre.id).exists()
