import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_tipos_custeio_list(jwt_authenticated_client_d, tipo_custeio_01, tipo_custeio_02):
    response = jwt_authenticated_client_d.get('/api/tipos-custeio/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'eh_tributos_e_tarifas': False,
            'nome': tipo_custeio_01.nome,
            'id': tipo_custeio_01.id,
            'uuid': f'{tipo_custeio_01.uuid}',
            'todas_unidades_selecionadas': True,
            'uso_associacao': 'Todas',
            'unidades': [],
        },
        {
            'eh_tributos_e_tarifas': False,
            'nome': tipo_custeio_02.nome,
            'id': tipo_custeio_02.id,
            'uuid': f'{tipo_custeio_02.uuid}',
            'todas_unidades_selecionadas': True,
            'uso_associacao': 'Todas',
            'unidades': [],
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_tipos_custeio_list_filtra_por_nome(jwt_authenticated_client_d, tipo_custeio_01, tipo_custeio_02):
    response = jwt_authenticated_client_d.get('/api/tipos-custeio/?nome=01', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert [item['nome'] for item in result] == [tipo_custeio_01.nome]


def test_api_tipos_custeio_list_filtra_por_unidade_vinculada(
        jwt_authenticated_client_d, tipo_custeio_factory, unidade_factory):
    unidade_alvo = unidade_factory()
    outra_unidade = unidade_factory()

    tipo_geral = tipo_custeio_factory(nome='Geral - sem restrição de unidade')
    tipo_vinculado_ao_alvo = tipo_custeio_factory(nome='Vinculado à unidade alvo')
    tipo_vinculado_ao_alvo.unidades.add(unidade_alvo)
    tipo_de_outra_unidade = tipo_custeio_factory(nome='Vinculado a outra unidade')
    tipo_de_outra_unidade.unidades.add(outra_unidade)

    response = jwt_authenticated_client_d.get(
        f'/api/tipos-custeio/?unidades__uuid={unidade_alvo.uuid}', content_type='application/json')
    result = json.loads(response.content)

    nomes_retornados = {item['nome'] for item in result}
    assert response.status_code == status.HTTP_200_OK
    assert nomes_retornados == {tipo_geral.nome, tipo_vinculado_ao_alvo.nome}
    assert tipo_de_outra_unidade.nome not in nomes_retornados
