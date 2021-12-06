import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_verifica_reajustes(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):

    response = jwt_authenticated_client_a.get(
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1.uuid}/verifica-reajustes/',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = [{
        "uuid": f'{analise_valor_reprogramado_por_acao.uuid}',
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": {
            'nome': f'{conta_associacao.tipo_conta.nome}',
            'uuid': f'{conta_associacao.uuid}'
        },
        "acao_associacao": {
            'nome': f'{acao_associacao.acao.nome}',
            'uuid': f'{acao_associacao.uuid}'
        },
        "novo_saldo_reprogramado_custeio": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_custeio}',
        "novo_saldo_reprogramado_capital": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_capital}',
        "novo_saldo_reprogramado_livre": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_livre}',
        "valor_saldo_reprogramado_correto": False
    }]

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


def test_action_saldos_iniciais_com_ajuste(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):

    response = jwt_authenticated_client_a.get(
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1.uuid}/saldos-iniciais-com-ajustes/?conta_associacao={conta_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = [{
        "uuid": f'{analise_valor_reprogramado_por_acao.uuid}',
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": {
            'nome': f'{conta_associacao.tipo_conta.nome}',
            'uuid': f'{conta_associacao.uuid}'
        },
        "acao_associacao": {
            'nome': f'{acao_associacao.acao.nome}',
            'uuid': f'{acao_associacao.uuid}'
        },
        "novo_saldo_reprogramado_custeio": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_custeio}',
        "novo_saldo_reprogramado_capital": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_capital}',
        "novo_saldo_reprogramado_livre": f'{analise_valor_reprogramado_por_acao.novo_saldo_reprogramado_livre}',
        "valor_saldo_reprogramado_correto": False
    }]

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


def test_action_get_saldos_iniciais_com_ajuste_sem_conta_associacao(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1.uuid}/saldos-iniciais-com-ajustes/',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid da conta da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert esperado == result
