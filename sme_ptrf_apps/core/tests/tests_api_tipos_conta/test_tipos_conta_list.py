import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_conta(tipo_conta_factory):
    return tipo_conta_factory(nome='Teste', agencia='', banco_nome='', numero_cartao='', numero_conta='', )


def test_api_list_tipos_conta(jwt_authenticated_client_a, tipo_conta):
    response = jwt_authenticated_client_a.get('/api/tipos-conta/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'agencia': '',
            'banco_nome': '',
            'id': tipo_conta.id,
            'nome': 'Teste',
            'numero_cartao': '',
            'numero_conta': '',
            'permite_inativacao': False,
            'apenas_leitura': tipo_conta.apenas_leitura,
            'uuid': f'{tipo_conta.uuid}',
            'recurso': f"{tipo_conta.recurso.uuid}",
            'recurso_completo': {
                'id': tipo_conta.recurso.id,
                'nome': tipo_conta.recurso.nome,
                'uuid': f"{tipo_conta.recurso.uuid}",
                'nome_exibicao': tipo_conta.recurso.nome_exibicao,
                'criado_em': f'{tipo_conta.recurso.criado_em.isoformat()}' if tipo_conta.recurso.criado_em else None,
                'alterado_em': f'{tipo_conta.recurso.alterado_em.isoformat()}' if tipo_conta.recurso.alterado_em else None,
                'cor': tipo_conta.recurso.cor,
                'icone': tipo_conta.recurso.icone if tipo_conta.recurso.icone else None,
                'ativo': tipo_conta.recurso.ativo,
                'legado': tipo_conta.recurso.legado,
                'exibe_valores_reprogramados': tipo_conta.recurso.exibe_valores_reprogramados
            }
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
