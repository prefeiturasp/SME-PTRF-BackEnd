import json

import pytest
from model_bakery import baker
from rest_framework import status

from ....dre.models import VerificacaoRegularidadeAssociacao, AnaliseRegularidadeAssociacao

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
def item_verificacao_regularidade_documentos_associacao_rais(lista_verificacao_regularidade_documentos_associacao):
    return baker.make(
        'dre.ItemVerificacaoRegularidade',
        descricao='RAIS',
        lista=lista_verificacao_regularidade_documentos_associacao
    )


@pytest.fixture
def ano_analise_regularidade_2021():
    return baker.make('AnoAnaliseRegularidade', ano=2021)


@pytest.fixture
def analise_regularidade_associacao(
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
def verificacao_regularidade_associacao_documento_cnpj(item_verificacao_regularidade_documentos_associacao_cnpj,
                                                       analise_regularidade_associacao):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        analise_regularidade=analise_regularidade_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj,
        regular=True
    )


@pytest.fixture
def verificacao_regularidade_associacao_documento_rais(item_verificacao_regularidade_documentos_associacao_rais,
                                                       analise_regularidade_associacao):
    return baker.make(
        'dre.VerificacaoRegularidadeAssociacao',
        analise_regularidade=analise_regularidade_associacao,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_rais,
        regular=True
    )


def test_atualiza_itens_verificacao_existentes(jwt_authenticated_client_a,
                                               associacao,
                                               grupo_verificacao_regularidade_documentos,
                                               lista_verificacao_regularidade_documentos_associacao,
                                               item_verificacao_regularidade_documentos_associacao_cnpj,
                                               item_verificacao_regularidade_documentos_associacao_rais,
                                               verificacao_regularidade_associacao_documento_cnpj,
                                               verificacao_regularidade_associacao_documento_rais,
                                               ano_analise_regularidade_2021,
                                               analise_regularidade_associacao
                                               ):
    payload = {
        'itens': [
            {
                "uuid": f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
                'regular': False
            },
            {
                "uuid": f'{item_verificacao_regularidade_documentos_associacao_rais.uuid}',
                'regular': True
            },
        ],
        'motivo_nao_regularidade': '',
        'ano': 2021
    }

    url = f'/api/associacoes/{associacao.uuid}/atualiza-itens-verificacao/'
    response = jwt_authenticated_client_a.post(url, data=json.dumps(payload), content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'mensagem': 'Itens de verificação atualizados.'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    analise_regularidade = AnaliseRegularidadeAssociacao.objects.get(
        associacao=associacao,
        ano_analise=ano_analise_regularidade_2021
    )
    verificacao1 = VerificacaoRegularidadeAssociacao.objects.filter(
        analise_regularidade=analise_regularidade,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_cnpj
    )
    assert verificacao1.count() == 0, 'Esse item não deveria existir'

    verificacao2 = VerificacaoRegularidadeAssociacao.objects.filter(
        analise_regularidade=analise_regularidade,
        item_verificacao=item_verificacao_regularidade_documentos_associacao_rais
    )
    assert verificacao2.count() == 1, 'Esse item deveria existir'


def test_atualiza_itens_verificacao_associacao_regular(
    jwt_authenticated_client_a,
    associacao,
    item_verificacao_regularidade_documentos_associacao_cnpj,
    item_verificacao_regularidade_documentos_associacao_rais,
    ano_analise_regularidade_2021,
):

    payload = {
        'itens': [
            {
                "uuid": f'{item_verificacao_regularidade_documentos_associacao_cnpj.uuid}',
                'regular': True
            },
            {
                "uuid": f'{item_verificacao_regularidade_documentos_associacao_rais.uuid}',
                'regular': True
            },
        ],
        'motivo_nao_regularidade': '',
        'ano': 2021
    }

    response = jwt_authenticated_client_a.post(
        f'/api/associacoes/{associacao.uuid}/atualiza-itens-verificacao/', data=json.dumps(payload),
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'associacao': f'{associacao.uuid}',
        'mensagem': 'Itens de verificação atualizados.'
    }

    from sme_ptrf_apps.dre.models import AnaliseRegularidadeAssociacao

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

    analise = AnaliseRegularidadeAssociacao.objects.get(
        associacao=associacao,
        ano_analise=ano_analise_regularidade_2021
    )
    assert analise.status_regularidade == 'REGULAR', "O status deveria estar regular."
