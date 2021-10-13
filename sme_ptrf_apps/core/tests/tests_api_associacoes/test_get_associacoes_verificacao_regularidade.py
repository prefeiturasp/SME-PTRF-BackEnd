import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def grupo_verificacao_regularidade_documentos():
    return baker.make('dre.GrupoVerificacaoRegularidade', titulo='Documentos')


@pytest.fixture
def lista_verificacao_regularidade_documentos_associacao(grupo_verificacao_regularidade_documentos):
    return baker.make(
        'dre.ListaVerificacaoRegularidade',
        titulo='Documentos da Associação',
        grupo=grupo_verificacao_regularidade_documentos
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_cnpj(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'dre.ItemVerificacaoRegularidade',
        descricao='CNPJ',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj(grupo_verificacao_regularidade_documentos,
                                                       lista_verificacao_regularidade_documentos_associacao,
                                                       item_verificacao_regularidade_documentos_associacao_cnpj,
                                                       associacao):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        associacao=associacao,
        grupo_verificacao=grupo_verificacao_regularidade_documentos,
        lista_verificacao=lista_verificacao_regularidade_documentos_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


def test_api_get_associacoes_verificacao_regularidade(jwt_authenticated_client_a, associacao,
                                                      grupo_verificacao_regularidade_documentos,
                                                      lista_verificacao_regularidade_documentos_associacao,
                                                      item_verificacao_regularidade_documentos_associacao_cnpj,
                                                      verificacao_regularidade_associacao_documento_cnpj
                                                      ):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/verificacao-regularidade/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'uuid': f'{associacao.uuid}',
        'motivo_nao_regularidade': '',
        'verificacao_regularidade': {
            'grupos_verificacao': [
                {
                    'uuid': f'{grupo_verificacao_regularidade_documentos.uuid}',
                    'titulo': grupo_verificacao_regularidade_documentos.titulo,
                    'listas_verificacao': [
                        {
                            'uuid': f'{lista_verificacao_regularidade_documentos_associacao.uuid}',
                            'titulo': lista_verificacao_regularidade_documentos_associacao.titulo,
                            'itens_verificacao': [
                                {
                                    'uuid': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
                                    'descricao': item_verificacao_regularidade_documentos_associacao_cnpj.descricao,
                                    'regular': True
                                },
                            ],
                            'status_lista_verificacao': 'Regular'
                        },
                    ]

                },
            ]
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
