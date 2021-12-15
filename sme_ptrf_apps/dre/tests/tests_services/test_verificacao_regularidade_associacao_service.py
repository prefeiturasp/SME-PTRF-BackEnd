import pytest
from model_bakery import baker

from ...services import get_verificacao_regularidade_associacao

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
def analise_regularidade_associacao_rais_regular(
    associacao,
    ano_analise_regularidade_2021
):
    return baker.make(
        'AnaliseRegularidadeAssociacao',
        associacao=associacao,
        ano_analise=ano_analise_regularidade_2021,
        status_regularidade='REGULAR'
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_cnpj_regular(
    grupo_verificacao_regularidade_documentos,
    lista_verificacao_regularidade_documentos_associacao,
    item_verificacao_regularidade_documentos_associacao_cnpj,
    analise_regularidade_associacao_rais_regular,
):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        analise_regularidade=analise_regularidade_associacao_rais_regular,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


@pytest.fixture
def item_verificacao_regularidade_documentos_associacao_rais(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'dre.ItemVerificacaoRegularidade',
        descricao='RAIS',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def analise_regularidade_associacao_rais_irregular(
    associacao,
    ano_analise_regularidade_2021
):
    return baker.make(
        'AnaliseRegularidadeAssociacao',
        associacao=associacao,
        ano_analise=ano_analise_regularidade_2021,
        status_regularidade='PENDENTE'
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_rais_irregular(
    item_verificacao_regularidade_documentos_associacao_rais,
    analise_regularidade_associacao_rais_irregular
):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        analise_regularidade=analise_regularidade_associacao_rais_irregular,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_rais,
        regular=False
    )


def test_verificacao_regularidade_associacao_regular(
    client,
    grupo_verificacao_regularidade_documentos,
    lista_verificacao_regularidade_documentos_associacao,
    item_verificacao_regularidade_documentos_associacao_cnpj,
    verificacao_regularidade_associacao_documento_cnpj_regular,
):
    analise = verificacao_regularidade_associacao_documento_cnpj_regular.analise_regularidade
    associacao = analise.associacao

    result = get_verificacao_regularidade_associacao(associacao.uuid, 2021)

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
                            'titulo': f'{lista_verificacao_regularidade_documentos_associacao.titulo}',
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

    assert result == esperado


def test_verificacao_regularidade_associacao_pendente_quando_sem_verificacao(client, associacao,
                                                                             grupo_verificacao_regularidade_documentos,
                                                                             lista_verificacao_regularidade_documentos_associacao,
                                                                             item_verificacao_regularidade_documentos_associacao_cnpj
                                                                             ):
    result = get_verificacao_regularidade_associacao(associacao.uuid, 2021)

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
                            'titulo': f'{lista_verificacao_regularidade_documentos_associacao.titulo}',
                            'itens_verificacao': [
                                {
                                    'uuid': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
                                    'descricao': item_verificacao_regularidade_documentos_associacao_cnpj.descricao,
                                    'regular': False
                                },
                            ],
                            'status_lista_verificacao': 'Pendente'
                        },
                    ]

                },
            ]
        }
    }

    assert result == esperado


def test_verificacao_regularidade_associacao_pendente_quando_com_verificacao_irregular(client, associacao,
                                                                                       grupo_verificacao_regularidade_documentos,
                                                                                       lista_verificacao_regularidade_documentos_associacao,
                                                                                       item_verificacao_regularidade_documentos_associacao_cnpj,
                                                                                       item_verificacao_regularidade_documentos_associacao_rais,
                                                                                       verificacao_regularidade_associacao_documento_cnpj_regular,
                                                                                       verificacao_regularidade_associacao_documento_rais_irregular
                                                                                       ):
    result = get_verificacao_regularidade_associacao(associacao.uuid, 2021)

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
                            'titulo': f'{lista_verificacao_regularidade_documentos_associacao.titulo}',
                            'itens_verificacao': [
                                {
                                    'uuid': f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
                                    'descricao': item_verificacao_regularidade_documentos_associacao_cnpj.descricao,
                                    'regular': True
                                },
                                {
                                    'uuid': f'{item_verificacao_regularidade_documentos_associacao_rais.uuid}',
                                    'descricao': item_verificacao_regularidade_documentos_associacao_rais.descricao,
                                    'regular': False
                                },
                            ],
                            'status_lista_verificacao': 'Pendente'
                        },
                    ]

                },
            ]
        }
    }

    assert result == esperado
