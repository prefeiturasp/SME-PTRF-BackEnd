import pytest

from rest_framework import status

from ...models import MembroComissao

pytestmark = pytest.mark.django_db


def test_delete_membro_comissao(
    jwt_authenticated_client_dre,
    membro_alex_comissao_a_dre_x
):
    assert MembroComissao.objects.filter(uuid=membro_alex_comissao_a_dre_x.uuid).exists()

    response = jwt_authenticated_client_dre.delete(
        f'/api/membros-comissoes/{membro_alex_comissao_a_dre_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not MembroComissao.objects.filter(uuid=membro_alex_comissao_a_dre_x.uuid).exists()
