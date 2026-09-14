import pytest
from rest_framework import status
from sme_ptrf_apps.despesas.models import Despesa, RateioDespesa
from sme_ptrf_apps.receitas.models import Receita
import json
from uuid import uuid4

pytestmark = pytest.mark.django_db


def test_api_conciliar_despesa_sem_periodo(jwt_authenticated_client_a, conta_associacao_cartao, despesa_2020_1):
    url = f'/api/conciliacoes/conciliar-despesa/?conta_associacao={conta_associacao_cartao.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_conciliar_despesa_periodo_nao_encontrado(jwt_authenticated_client_a, conta_associacao_cartao, despesa_2020_1):
    url = f'/api/conciliacoes/conciliar-despesa/?periodo={uuid4()}&conta_associacao={conta_associacao_cartao.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_conciliar_despesa_sem_conta_associacao(jwt_authenticated_client_a, periodo_2020_1, despesa_2020_1):
    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_conciliar_despesa_conta_associacao_nao_encontrada(jwt_authenticated_client_a, periodo_2020_1, despesa_2020_1):
    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}&conta_associacao={uuid4()}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_conciliar_despesa_sem_transacao(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_desconciliar_despesa_sem_periodo(jwt_authenticated_client_a, conta_associacao_cartao, despesa_2020_1):
    url = f'/api/conciliacoes/desconciliar-despesa/?conta_associacao={conta_associacao_cartao.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_desconciliar_despesa_periodo_nao_encontrado(jwt_authenticated_client_a, conta_associacao_cartao, despesa_2020_1):
    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={uuid4()}&conta_associacao={conta_associacao_cartao.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_desconciliar_despesa_sem_conta_associacao(jwt_authenticated_client_a, periodo_2020_1, despesa_2020_1):
    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_desconciliar_despesa_conta_associacao_nao_encontrada(jwt_authenticated_client_a, periodo_2020_1, despesa_2020_1):
    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}&conta_associacao={uuid4()}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_api_desconciliar_despesa_sem_transacao(jwt_authenticated_client_a, periodo_2020_1, conta_associacao_cartao):
    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_api_deve_conciliar_transacao_despesa(
    jwt_authenticated_client_a,
    acao_associacao_role_cultural,
    despesa_2020_1,
    rateio_despesa_2020_role_nao_conferido,
    rateio_despesa_2020_ptrf_conferido,
    periodo_2020_1,
    conta_associacao_cartao

):

    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url = f'{url}&conta_associacao={conta_associacao_cartao.uuid}'
    url = f'{url}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    despesa_conciliada = Despesa.by_uuid(despesa_2020_1.uuid)
    rateio_conciliado = RateioDespesa.by_uuid(rateio_despesa_2020_role_nao_conferido.uuid)

    assert response.status_code == status.HTTP_200_OK

    assert despesa_conciliada.conferido, "Despesa deveria ter sido marcada como conferida."
    assert rateio_conciliado.conferido, "Rateio deveria ter sido marcado como conferido."
    assert rateio_conciliado.periodo_conciliacao == periodo_2020_1, "Rateio deveria ter sido vinculada ao período."


def test_api_nao_deve_conciliar_transacao_receita(
    jwt_authenticated_client_a,
    acao_associacao_role_cultural,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    periodo_2020_1,
    conta_associacao_cartao

):

    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url = f'{url}&conta_associacao={conta_associacao_cartao.uuid}'
    url = f'{url}&transacao={receita_2020_1_role_outras_nao_conferida.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')
    result = json.loads(response.content)

    receita_conciliada = Receita.by_uuid(receita_2020_1_role_outras_nao_conferida.uuid)
    esperado = {
        "erro": "Gasto não encontrado.",
        "mensagem": f"O objeto de gasto para o uuid {receita_conciliada.uuid} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_api_deve_desconciliar_transacao_despesa(
    jwt_authenticated_client_a,
    acao_associacao_role_cultural,
    despesa_2020_1,
    rateio_despesa_2020_role_nao_conferido,
    rateio_despesa_2020_ptrf_conferido,
    periodo_2020_1,
    conta_associacao_cartao

):

    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url = f'{url}&conta_associacao={conta_associacao_cartao.uuid}'
    url = f'{url}&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')

    despesa_desconciliada = Despesa.by_uuid(despesa_2020_1.uuid)
    rateio_desconciliado = RateioDespesa.by_uuid(rateio_despesa_2020_ptrf_conferido.uuid)

    assert response.status_code == status.HTTP_200_OK

    assert not despesa_desconciliada.conferido, "Despesa deveria ter sido desconciliada."
    assert not rateio_desconciliado.conferido, "Rateio deveria ter sido desconciliado."
    assert rateio_desconciliado.periodo_conciliacao is None, "Período deveria ter sido desvinculado."


def test_api_nao_deve_desconciliar_transacao_receita(
    jwt_authenticated_client_a,
    acao_associacao_role_cultural,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    periodo_2020_1,
    conta_associacao_cartao

):

    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'
    url += f'&transacao={receita_2020_1_ptrf_repasse_conferida.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')
    result = json.loads(response.content)

    receita_desconciliada = Receita.by_uuid(receita_2020_1_ptrf_repasse_conferida.uuid)
    esperado = {
        "erro": "Gasto não encontrado.",
        "mensagem": f"O objeto de Gasto para o uuid {receita_desconciliada.uuid} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado


def test_api_nao_deve_conciliar_transacao_quando_prestacao_existente(
    jwt_authenticated_client_a,
    despesa_2020_1,
    periodo_2020_1,
    conta_associacao_cartao,
    prestacao_conta_2020_1_devolvida,
):
    url = f'/api/conciliacoes/conciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'
    url += f'&transacao={despesa_2020_1.uuid}'

    response = jwt_authenticated_client_a.patch(url, content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'periodo_bloqueado.',
        'mensagem': "Não é possível realizar conciliação de despesa. A prestação de contas já foi iniciada"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado

def test_api_nao_deve_desconciliar_transacao_quando_prestacao_existente(
    jwt_authenticated_client_a,
    despesa_2020_1,
    periodo_2020_1,
    conta_associacao_cartao,
    prestacao_conta_2020_1_conciliada
):   

    url = f'/api/conciliacoes/desconciliar-despesa/?periodo={periodo_2020_1.uuid}'
    url += f'&conta_associacao={conta_associacao_cartao.uuid}'
    url += f'&transacao={despesa_2020_1.uuid}'    
    
    response = jwt_authenticated_client_a.patch(url, content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'periodo_bloqueado.',
        'mensagem': "Não é possível realizar desconciliação de despesa. A prestação de contas já foi iniciada"
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
