import datetime
import json

import pytest
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.choices import StatusTag

pytestmark = pytest.mark.django_db


@pytest.fixture
def despesa_fornecedor_a(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor A graça ARVORE',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def despesa_fornecedor_b(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='517.870.110-03',
        nome_fornecedor='Fornecedor B Graca valença',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )

@pytest.fixture
def despesa_inativa_fornecedor_b(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='654321',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='517.870.110-03',
        nome_fornecedor='Fornecedor B Graca valença',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
        data_e_hora_de_inativacao=datetime.datetime(2022, 9, 6, 10, 30, 0)
    )


def test_api_get_despesas_filtro_por_cnpj_cpf_fornecedor(jwt_authenticated_client_d, associacao, despesa_fornecedor_a,
                                                         despesa_fornecedor_b, despesa_inativa_fornecedor_b):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=11.478.276/0001-04',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo CNPJ.'

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=517.870.110-03',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo CPF'

    response = jwt_authenticated_client_d.get(
        f'/api/rateios-despesas/?associacao__uuid={associacao.uuid}&cpf_cnpj_fornecedor=343646',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_filtro_por_tipo_documento(jwt_authenticated_client_d, associacao, despesa_fornecedor_a,
                                                    despesa_fornecedor_b, tipo_documento):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?tipo_documento__uuid={tipo_documento.uuid}', content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2, 'Deve localizar pelo Tipo de documento.'

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?tipo_documento__uuid={despesa_fornecedor_b.uuid}',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_filtro_por_numero_documento(jwt_authenticated_client_d, associacao, despesa_fornecedor_a,
                                                      despesa_fornecedor_b, tipo_documento):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?numero_documento=123456', content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve localizar pelo número do documento.'

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?numero_documento=999999',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


def test_api_get_despesas_campos(jwt_authenticated_client_d, associacao, despesa_fornecedor_a,
                                 despesa_fornecedor_b, tipo_documento, tipo_transacao):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?numero_documento=123456', content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    esperado = [
        {
            'uuid': f'{despesa_fornecedor_a.uuid}',
            'associacao': f'{associacao.uuid}',
            'numero_documento': '123456',
            'status': f'{despesa_fornecedor_a.status}',
            'tipo_documento': {
                'id': tipo_documento.id,
                'nome': 'NFe',
            },
            'data_documento': '2020-03-10',
            'cpf_cnpj_fornecedor': '11.478.276/0001-04',
            'nome_fornecedor': 'Fornecedor A graça ARVORE',
            'valor_total': '100.00',
            'valor_ptrf': 90.0,
            'data_transacao': '2020-03-10',
            'despesa_geradora_do_imposto': None,
            'despesas_impostos': [],
            'tipo_transacao': {
                'id': tipo_transacao.id,
                'nome': tipo_transacao.nome,
                'tem_documento': tipo_transacao.tem_documento
            },
            'documento_transacao': '',
            'informacoes': [{'tag_hint': 'Parte da despesa foi paga com recursos '
                                         'próprios ou por mais de uma conta.',
                             'tag_id': '3',
                             'tag_nome': 'Parcial'},
                            {'tag_hint': 'Essa despesa já possui conciliação bancária.',
                             'tag_id': '9',
                             'tag_nome': 'Conciliada'}
                            ],
            'rateios': [],
            'receitas_saida_do_recurso': None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado, 'Não retornou o esperado.'


def test_api_get_despesas_filtro_por_tipo_documento_id(jwt_authenticated_client_d, associacao, despesa_fornecedor_a,
                                                       despesa_fornecedor_b, tipo_documento):
    url = f'/api/despesas/?tipo_documento__id={tipo_documento.id}'
    response = jwt_authenticated_client_d.get(url, content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2, 'Deve localizar pelo Tipo de documento.'

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?tipo_documento__id=87878',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 0, 'Não deveria ter achado nada'


@pytest.fixture
def tag_teste_filtro_por_tag():
    return baker.make(
        'Tag',
        nome="COVID-19",
        status=StatusTag.ATIVO.name
    )


@pytest.fixture
def despesa_teste_filtro_por_tag(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='777777',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='517.870.110-03',
        nome_fornecedor='Fornecedor Teste Filtro Por Tag',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_tag_teste_filtro_por_tag(associacao, despesa_teste_filtro_por_tag, conta_associacao, acao,
                                            tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_servico,
                                            especificacao_instalacao_eletrica, acao_associacao_ptrf,
                                            tag_teste_filtro_por_tag):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_teste_filtro_por_tag,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        conferido=True,
        tag=tag_teste_filtro_por_tag,
    )


def test_api_get_despesas_filtro_por_tag(jwt_authenticated_client_d, associacao, despesa_teste_filtro_por_tag,
                                         tipo_documento, tipo_transacao, rateio_despesa_tag_teste_filtro_por_tag,
                                         tag_teste_filtro_por_tag):
    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?rateios__tag__uuid={tag_teste_filtro_por_tag.uuid}',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1, 'Deve encontrar pela tag_teste_filtro_por_tag'


@pytest.fixture
def despesa_teste_filtro_vinculo_atividade_tag_1(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='2131232',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='517.870.110-03',
        nome_fornecedor='Fornecedor Teste Filtro Vinculo Atividade tag 1',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=120.00,
    )

@pytest.fixture
def despesa_teste_filtro_vinculo_atividade_tag_2(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='4123123',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='31.066.747/0001-76',
        nome_fornecedor='Fornecedor Teste Filtro Vinculo Atividade tag 2',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=130.00,
    )

@pytest.fixture
def despesa_teste_filtro_vinculo_atividade_sem_tag(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='57454757',
        data_documento=datetime.date(2020, 3, 11),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='90.032.744/0001-80',
        nome_fornecedor='Fornecedor Teste Filtro Vinculo Atividade sem tag',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 11),
        valor_total=140.00,
    )

@pytest.fixture
def tag_1():
    return baker.make(
        'Tag',
        id=1,
        nome="TAG TESTE 1",
        status=StatusTag.ATIVO.name
    )

@pytest.fixture
def tag_2():
    return baker.make(
        'Tag',
        id=2,
        nome="TAG TESTE 2",
        status=StatusTag.ATIVO.name
    )

@pytest.fixture
def rateio_despesa_tag_1(associacao, despesa_teste_filtro_vinculo_atividade_tag_1, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_servico, especificacao_instalacao_eletrica, acao_associacao_ptrf, tag_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_teste_filtro_vinculo_atividade_tag_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=120.00,
        conferido=True,
        tag=tag_1,
    )

@pytest.fixture
def rateio_despesa_tag_2(associacao, despesa_teste_filtro_vinculo_atividade_tag_2, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_servico, especificacao_instalacao_eletrica, acao_associacao_ptrf, tag_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_teste_filtro_vinculo_atividade_tag_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=130.00,
        conferido=True,
        tag=tag_1,
    )

@pytest.fixture
def rateio_despesa_sem_tag(associacao, despesa_teste_filtro_vinculo_atividade_sem_tag, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_servico, especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_teste_filtro_vinculo_atividade_sem_tag,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=140.00,
        conferido=True,
    )

def test_api_get_despesas_filtro_vinculo_de_atividades_vazio(jwt_authenticated_client_d, associacao, despesa_teste_filtro_vinculo_atividade_tag_1, despesa_teste_filtro_vinculo_atividade_tag_2, despesa_teste_filtro_vinculo_atividade_sem_tag, tipo_documento, tipo_transacao, rateio_despesa_tag_1, rateio_despesa_tag_2, rateio_despesa_sem_tag, tag_1, tag_2):

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?filtro_vinculo_atividades=',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 3, 'Deve encontrar todas as três despesas.'


def test_api_get_despesas_filtro_vinculo_de_atividades_com_tag_1_e_tag_2(jwt_authenticated_client_d, associacao, despesa_teste_filtro_vinculo_atividade_tag_1, despesa_teste_filtro_vinculo_atividade_tag_2, despesa_teste_filtro_vinculo_atividade_sem_tag, tipo_documento, tipo_transacao, rateio_despesa_tag_1, rateio_despesa_tag_2, rateio_despesa_sem_tag, tag_1, tag_2):

    response = jwt_authenticated_client_d.get(
        f'/api/despesas/?filtro_vinculo_atividades=1,2',
        content_type='application/json')
    result = json.loads(response.content)
    result = result["results"]

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2, 'Deve encontrar duas despesas a de tag_1 e a de tag_2.'
