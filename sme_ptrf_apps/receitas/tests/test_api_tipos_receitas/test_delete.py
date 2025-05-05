
import json

import pytest
from rest_framework import status

from sme_ptrf_apps.receitas.models import TipoReceita


pytestmark = pytest.mark.django_db


def test_delete_sucesso(jwt_authenticated_client_p, tipo_receita_estorno): 
    response = jwt_authenticated_client_p.delete(f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/',
                                                 content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert TipoReceita.objects.count() == 0


def test_delete_erro_uuid_invalido(jwt_authenticated_client_p, tipo_receita_estorno): 
    response = jwt_authenticated_client_p.delete(f'/api/tipos-receitas/8a51f351-1335-4d89-8078-87c75f7999ce/',
                                                 content_type='application/json')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert TipoReceita.objects.count() == 1


def test_delete_erro_protected_model(jwt_authenticated_client_p, receita): 
    response = jwt_authenticated_client_p.delete(f'/api/tipos-receitas/{receita.tipo_receita.uuid}/',
                                                 content_type='application/json')

    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert TipoReceita.objects.count() == 1
    assert content == {
        'erro': 'ProtectedError',
        'mensagem': 'Esse tipo de crédito não pode ser excluído pois existem receitas cadastradas com esse tipo.'
    }