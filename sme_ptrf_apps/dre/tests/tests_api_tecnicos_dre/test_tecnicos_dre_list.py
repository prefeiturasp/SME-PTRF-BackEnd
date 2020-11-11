import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_tecnicos_dre_todos(jwt_authenticated_client_dre, tecnico_jose_dre_ipiranga, tecnico_maria_dre_butantan):
    response = jwt_authenticated_client_dre.get(f'/api/tecnicos-dre/', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            "uuid": f'{tecnico_jose_dre_ipiranga.uuid}',
            "nome": tecnico_jose_dre_ipiranga.nome,
            "rf": tecnico_jose_dre_ipiranga.rf,
            "email": tecnico_jose_dre_ipiranga.email,
            "telefone": tecnico_jose_dre_ipiranga.telefone,
            "dre": {
                'uuid': f'{tecnico_jose_dre_ipiranga.dre.uuid}',
                'codigo_eol': f'{tecnico_jose_dre_ipiranga.dre.codigo_eol}',
                'tipo_unidade': f'{tecnico_jose_dre_ipiranga.dre.tipo_unidade}',
                'nome': f'{tecnico_jose_dre_ipiranga.dre.nome}',
                'sigla': f'{tecnico_jose_dre_ipiranga.dre.sigla}',
            },
        },
        {
            "uuid": f'{tecnico_maria_dre_butantan.uuid}',
            "nome": tecnico_maria_dre_butantan.nome,
            "rf": tecnico_maria_dre_butantan.rf,
            "email": tecnico_maria_dre_butantan.email,
            "telefone": tecnico_maria_dre_butantan.telefone,
            "dre": {
                'uuid': f'{tecnico_maria_dre_butantan.dre.uuid}',
                'codigo_eol': f'{tecnico_maria_dre_butantan.dre.codigo_eol}',
                'tipo_unidade': f'{tecnico_maria_dre_butantan.dre.tipo_unidade}',
                'nome': f'{tecnico_maria_dre_butantan.dre.nome}',
                'sigla': f'{tecnico_maria_dre_butantan.dre.sigla}',
            },
        }

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_tecnicos_dre_ipiranga(jwt_authenticated_client_dre, tecnico_jose_dre_ipiranga, tecnico_maria_dre_butantan, dre_ipiranga):
    response = jwt_authenticated_client_dre.get(f'/api/tecnicos-dre/?dre__uuid={dre_ipiranga.uuid}', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            "uuid": f'{tecnico_jose_dre_ipiranga.uuid}',
            "nome": tecnico_jose_dre_ipiranga.nome,
            "rf": tecnico_jose_dre_ipiranga.rf,
            "email": tecnico_jose_dre_ipiranga.email,
            "telefone": tecnico_jose_dre_ipiranga.telefone,
            "dre": {
                'uuid': f'{tecnico_jose_dre_ipiranga.dre.uuid}',
                'codigo_eol': f'{tecnico_jose_dre_ipiranga.dre.codigo_eol}',
                'tipo_unidade': f'{tecnico_jose_dre_ipiranga.dre.tipo_unidade}',
                'nome': f'{tecnico_jose_dre_ipiranga.dre.nome}',
                'sigla': f'{tecnico_jose_dre_ipiranga.dre.sigla}',
            },
        }

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado


def test_api_list_tecnicos_dre_por_rf(jwt_authenticated_client_dre, tecnico_jose_dre_ipiranga, tecnico_maria_dre_butantan, dre_ipiranga):
    response = jwt_authenticated_client_dre.get(f'/api/tecnicos-dre/?rf={tecnico_jose_dre_ipiranga.rf}', content_type='application/json')
    result = json.loads(response.content)

    result_esperado = [
        {
            "uuid": f'{tecnico_jose_dre_ipiranga.uuid}',
            "nome": tecnico_jose_dre_ipiranga.nome,
            "rf": tecnico_jose_dre_ipiranga.rf,
            "email": tecnico_jose_dre_ipiranga.email,
            "telefone": tecnico_jose_dre_ipiranga.telefone,
            "dre": {
                'uuid': f'{tecnico_jose_dre_ipiranga.dre.uuid}',
                'codigo_eol': f'{tecnico_jose_dre_ipiranga.dre.codigo_eol}',
                'tipo_unidade': f'{tecnico_jose_dre_ipiranga.dre.tipo_unidade}',
                'nome': f'{tecnico_jose_dre_ipiranga.dre.nome}',
                'sigla': f'{tecnico_jose_dre_ipiranga.dre.sigla}',
            },
        }

    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado
