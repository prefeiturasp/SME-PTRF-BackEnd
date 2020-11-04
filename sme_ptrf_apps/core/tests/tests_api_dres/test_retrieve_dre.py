import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def _dre():
    return baker.make(
        'Unidade',
        uuid='f92d2caf-d71f-4ed0-87b2-6d326fb648a7',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='GUAIANASES',
        sigla='G'
    )


def test_api_retrieve_dre(jwt_authenticated_client_a, _dre):
    response = jwt_authenticated_client_a.get(f'/api/dres/{_dre.uuid}/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = {
        "uuid": f'{_dre.uuid}',
        "codigo_eol": f'{_dre.codigo_eol}',
        "tipo_unidade": f'{_dre.tipo_unidade}',
        "nome": f'{_dre.nome}',
        "sigla": f'{_dre.sigla}',
        "dre": None,
        "email": f'{_dre.email}',
        "telefone": f'{_dre.telefone}',
        "tipo_logradouro": f'{_dre.tipo_logradouro}',
        "logradouro": f'{_dre.logradouro}',
        "numero": f'{_dre.numero}',
        "complemento": f'{_dre.complemento}',
        "bairro": f'{_dre.bairro}',
        "cep": f'{_dre.cep}',
        "qtd_alunos": 0,
        "diretor_nome": f'{_dre.diretor_nome}',
        "dre_cnpj": f'{_dre.dre_cnpj}',
        "dre_diretor_regional_rf": f'{_dre.dre_diretor_regional_rf}',
        "dre_diretor_regional_nome": f'{_dre.dre_diretor_regional_nome}',
        "dre_designacao_portaria": f'{_dre.dre_designacao_portaria}',
        "dre_designacao_ano": f'{_dre.dre_designacao_ano}',
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
