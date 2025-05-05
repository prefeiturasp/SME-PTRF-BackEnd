import json
import pytest
from rest_framework import status
from sme_ptrf_apps.receitas.models import TipoReceita

pytestmark = pytest.mark.django_db


def test_patch_sucesso(jwt_authenticated_client_sme, tipo_receita_estorno):
    payload = {
        "nome": "Tipo receita 001",
        "e_repasse": True,
        "aceita_capital": True,
    }
    response = jwt_authenticated_client_sme.patch(f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/',
                                                  content_type='application/json',
                                                  data=json.dumps(payload))

    assert response.status_code == status.HTTP_200_OK
    assert TipoReceita.objects.filter(nome="Tipo receita 001").exists() is True
    assert TipoReceita.objects.filter(nome="Tipo receita 001").first().e_repasse is True
    assert TipoReceita.objects.filter(nome="Tipo receita 001").first().aceita_capital is True


def test_post_erro_nome_duplicado(jwt_authenticated_client_sme, tipo_receita_estorno, tipo_receita_repasse):
    payload = {
        "nome": "Repasse"
    }
    response = jwt_authenticated_client_sme.patch(f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/',
                                                  content_type='application/json',
                                                  data=json.dumps(payload))
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content == {'non_field_errors': 'Este Tipo de Receita já existe.'}
