import datetime
import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_verifica_saldo_antes_post_saldo_ok(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo,
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/',
                                               data=json.dumps(payload_despesa_valida),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo(
    jwt_authenticated_client_d,
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_outra_acao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
        'saldos_insuficientes': [
            {
                'acao': acao_associacao.acao.nome,
                'aplicacao': 'CUSTEIO',
                'conta': 'Cheque',
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_com_saldo_considerando_livre_aplicacao(
    jwt_authenticated_client_d,
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo_na_conta_com_parametro_nao_aceita_negativo(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_nao_aceita_saldo_negativo_em_conta
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_conta_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
        'saldos_insuficientes': [
            {
                'conta': conta_associacao.tipo_conta.nome,
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': False
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo_na_conta_com_parametro_aceita_negativo(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_aceita_saldo_negativo_em_conta
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_conta_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
        'saldos_insuficientes': [
            {
                'conta': conta_associacao.tipo_conta.nome,
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_com_saldo_na_conta_considerando_recursos_livre_aplicacao(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_nao_aceita_saldo_negativo_em_conta,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_despesa_anterior_periodo_inicial(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida_anterior_periodo_inicial,
    parametros_nao_aceita_saldo_negativo_em_conta,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/',
                                               data=json.dumps(payload_despesa_valida_anterior_periodo_inicial),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'lancamento_anterior_implantacao',
        'mensagem': 'Lançamento com data anterior ao período inicial da associação.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_historico_completo_sem_pc_sem_fechamento(
    jwt_authenticated_client_d,
    associacao,
    periodo_anterior,
    periodo_2020_1,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao_associacao,
    conta_associacao,
    tipo_receita_repasse,
    especificacao_material_servico,
    receita_factory,
):
    """
    Associação sem PC e sem fechamento: receitas no período inicial devem compor o saldo
    para despesa em período posterior (janela única do período atual não basta).
    """
    assert associacao.periodo_inicial_id == periodo_anterior.id
    assert periodo_2020_1.data_inicio_realizacao_despesas <= datetime.date(2020, 3, 10)

    receita_factory.create(
        associacao=associacao,
        data=datetime.date(2019, 2, 1),
        valor=5000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
    )

    payload = {
        'associacao': f'{associacao.uuid}',
        'tipo_documento': tipo_documento.id,
        'tipo_transacao': tipo_transacao.id,
        'numero_documento': '634767',
        'data_documento': '2020-03-10',
        'cpf_cnpj_fornecedor': '36.352.197/0001-75',
        'nome_fornecedor': 'FORNECEDOR TESTE SA',
        'data_transacao': '2020-03-10',
        'valor_total': 11000.50,
        'valor_recursos_proprios': 1000.50,
        'rateios': [
            {
                'associacao': f'{associacao.uuid}',
                'conta_associacao': f'{conta_associacao.uuid}',
                'acao_associacao': f'{acao_associacao.uuid}',
                'aplicacao_recurso': tipo_aplicacao_recurso,
                'tipo_custeio': tipo_custeio.id,
                'especificacao_material_servico': especificacao_material_servico.id,
                'valor_rateio': 1000.00,
                'quantidade_itens_capital': 2,
                'valor_item_capital': 500.00,
                'numero_processo_incorporacao_capital': '6234673223462364632',
            }
        ],
    }

    response = jwt_authenticated_client_d.post(
        '/api/rateios-despesas/verificar-saldos/',
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result['situacao_do_saldo'] == 'saldo_suficiente'
    assert result['saldos_insuficientes'] == []


def test_api_verifica_saldo_com_prestacao_conta_mantem_janela_entre_periodos(
    jwt_authenticated_client_d,
    associacao,
    periodo_anterior,
    periodo_2020_1,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao_associacao,
    conta_associacao,
    tipo_conta,
    tipo_receita_repasse,
    especificacao_material_servico,
    parametros_nao_aceita_saldo_negativo_em_conta,
    prestacao_conta_factory,
    receita_factory,
):
    """Com PC cadastrada, não aplica histórico completo: receita só no período anterior não cobre despesa no atual."""
    prestacao_conta_factory.create(
        associacao=associacao,
        periodo=periodo_anterior,
    )

    receita_factory.create(
        associacao=associacao,
        data=datetime.date(2019, 2, 1),
        valor=5000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
    )

    payload = {
        'associacao': f'{associacao.uuid}',
        'tipo_documento': tipo_documento.id,
        'tipo_transacao': tipo_transacao.id,
        'numero_documento': '634767',
        'data_documento': '2020-03-10',
        'cpf_cnpj_fornecedor': '36.352.197/0001-75',
        'nome_fornecedor': 'FORNECEDOR TESTE SA',
        'data_transacao': '2020-03-10',
        'valor_total': 11000.50,
        'valor_recursos_proprios': 1000.50,
        'rateios': [
            {
                'associacao': f'{associacao.uuid}',
                'conta_associacao': f'{conta_associacao.uuid}',
                'acao_associacao': f'{acao_associacao.uuid}',
                'aplicacao_recurso': tipo_aplicacao_recurso,
                'tipo_custeio': tipo_custeio.id,
                'especificacao_material_servico': especificacao_material_servico.id,
                'valor_rateio': 1000.00,
                'quantidade_itens_capital': 2,
                'valor_item_capital': 500.00,
                'numero_processo_incorporacao_capital': '6234673223462364632',
            }
        ],
    }

    response = jwt_authenticated_client_d.post(
        '/api/rateios-despesas/verificar-saldos/',
        data=json.dumps(payload),
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK
    result = json.loads(response.content)
    assert result['situacao_do_saldo'] == 'saldo_conta_insuficiente'
    assert result['saldos_insuficientes'] == [
        {
            'conta': tipo_conta.nome,
            'saldo_disponivel': 0,
            'total_rateios': 1000.00,
        }
    ]
