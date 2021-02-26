import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def monta_result_esperado(transacoes_esperadas, periodo, conta):
    result_esperado = []

    for transacao in transacoes_esperadas:

        mestre_esperado = {
            'associacao': f'{transacao["mestre"].associacao.uuid}',
            'numero_documento': transacao["mestre"].numero_documento,
            'tipo_documento': {
                'id': transacao["mestre"].tipo_documento.id,
                'nome': transacao["mestre"].tipo_documento.nome,
            },
            'tipo_transacao': {
                'id': transacao["mestre"].tipo_transacao.id,
                'nome': transacao["mestre"].tipo_transacao.nome,
                'tem_documento': transacao["mestre"].tipo_transacao.tem_documento,
            },
            'documento_transacao': f'{transacao["mestre"].documento_transacao}',
            'data_documento': f'{transacao["mestre"].data_documento}',
            'data_transacao': f'{transacao["mestre"].data_transacao}',
            'cpf_cnpj_fornecedor': transacao["mestre"].cpf_cnpj_fornecedor,
            'nome_fornecedor': transacao["mestre"].nome_fornecedor,
            'valor_ptrf': transacao["mestre"].valor_ptrf,
            'valor_total': f'{transacao["mestre"].valor_total:.2f}',
            'status': transacao["mestre"].status,
            'conferido': transacao["mestre"].conferido,
            'uuid': f'{transacao["mestre"].uuid}',

        } if transacao["tipo"] == 'Gasto' else {
            'associacao': f'{transacao["mestre"].associacao.uuid}',
            'acao_associacao': {
                'id': transacao["mestre"].acao_associacao.id,
                'nome': transacao["mestre"].acao_associacao.acao.nome,
                'e_recursos_proprios': transacao["mestre"].acao_associacao.acao.e_recursos_proprios,
                'uuid': f'{transacao["mestre"].acao_associacao.uuid}'
            },
            'categoria_receita': transacao["mestre"].categoria_receita,
            'tipo_receita': {'id': transacao["mestre"].tipo_receita.id, 'nome': transacao["mestre"].tipo_receita.nome},
            'detalhamento': transacao["mestre"].detalhamento,
            'data': f'{transacao["mestre"].data}',
            'valor': f'{transacao["mestre"].valor:.2f}',
            'conferido': transacao["mestre"].conferido,
            'notificar_dias_nao_conferido': transacao["mestre"].notificar_dias_nao_conferido,
            'uuid': f'{transacao["mestre"].uuid}',
        }

        rateios_esperados = []
        for rateio in transacao["rateios"]:
            rateio_esperado = {
                "tipo_custeio": {
                    'id': rateio.tipo_custeio.id,
                    'nome': rateio.tipo_custeio.nome,
                    'uuid': f"{rateio.tipo_custeio.uuid}"
                },
                "especificacao_material_servico": {
                    "id": rateio.especificacao_material_servico.id,
                    "descricao": rateio.especificacao_material_servico.descricao,
                    "aplicacao_recurso": rateio.aplicacao_recurso,
                    "tipo_custeio": rateio.tipo_custeio.id,
                },
                "notificar_dias_nao_conferido": rateio.notificar_dias_nao_conferido,
                "aplicacao_recurso": rateio.aplicacao_recurso,
                "acao_associacao": {
                    "uuid": f'{rateio.acao_associacao.uuid}',
                    "id": rateio.acao_associacao.id,
                    "nome": rateio.acao_associacao.acao.nome,
                    "e_recursos_proprios": rateio.acao_associacao.acao.e_recursos_proprios,
                },
                "conferido": rateio.conferido,
                "valor_rateio": f'{rateio.valor_rateio:.2f}',
                "uuid": f'{rateio.uuid}',
            }
            rateios_esperados.append(rateio_esperado)

        max_notificar_dias_nao_conferido = 0
        for rateio in rateios_esperados:
            if rateio['notificar_dias_nao_conferido'] > max_notificar_dias_nao_conferido:
                max_notificar_dias_nao_conferido = rateio['notificar_dias_nao_conferido']

        result_esperado.append(
            {
                'periodo': f'{periodo.uuid}',
                'conta': f'{conta.uuid}',
                'data': f'{transacao["mestre"].data_transacao if transacao["tipo"] == "Gasto" else transacao["mestre"].data}',
                'tipo_transacao': transacao["tipo"],
                'numero_documento': transacao["mestre"].numero_documento if transacao["tipo"] == "Gasto" else "",
                'descricao': transacao["mestre"].nome_fornecedor if transacao["tipo"] == "Gasto" else transacao[
                    "mestre"].tipo_receita.nome,
                'valor_transacao_total': transacao["mestre"].valor_total if transacao["tipo"] == "Gasto" else transacao[
                    "mestre"].valor,
                'valor_transacao_na_conta': transacao["valor_transacao_na_conta"],
                'valores_por_conta': transacao["valores_por_conta"],
                'documento_mestre': mestre_esperado,
                'rateios': rateios_esperados,
                'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido if transacao["tipo"] == "Gasto" else
                transacao["mestre"].notificar_dias_nao_conferido,
                'conferido': transacao["mestre"].conferido,
            }
        )

    return result_esperado


def test_api_get_transacoes_conferidas(jwt_authenticated_client_a,
                                       despesa_2020_1,
                                       rateio_despesa_2020_role_conferido,
                                       rateio_despesa_2020_ptrf_conferido,
                                       rateio_despesa_2020_role_cheque_conferido,
                                       periodo_2020_1,
                                       conta_associacao_cartao,
                                       receita_2020_1_ptrf_repasse_conferida,
                                       ):
    conta_uuid = conta_associacao_cartao.uuid

    transacoes_esperadas = [
        {
            'mestre': receita_2020_1_ptrf_repasse_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
        },
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 200.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 200.0
                },
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
        },

    ]

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=True'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_api_get_transacoes_nao_conferidas(jwt_authenticated_client_a,
                                           acao_associacao_role_cultural,
                                           despesa_2019_2,
                                           rateio_despesa_2019_role_conferido,
                                           despesa_2020_1,
                                           rateio_despesa_2020_role_nao_conferido,
                                           rateio_despesa_2020_ptrf_conferido,
                                           rateio_despesa_2020_role_cheque_conferido,
                                           receita_2020_1_ptrf_repasse_conferida,
                                           receita_2020_1_role_outras_nao_conferida,
                                           periodo_2020_1,
                                           conta_associacao_cartao
                                           ):
    conta_uuid = conta_associacao_cartao.uuid

    transacoes_esperadas = [
        {
            'mestre': receita_2020_1_role_outras_nao_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
        },
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_nao_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 200.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 200.0
                },
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
        },

    ]

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_deve_trazer_transacoes_nao_conferidas_de_periodos_anteriores(jwt_authenticated_client_a,
                                                                      acao_associacao_role_cultural,
                                                                      despesa_2019_2,
                                                                      rateio_despesa_2019_role_conferido,
                                                                      rateio_despesa_2019_role_nao_conferido,
                                                                      despesa_2020_1,
                                                                      rateio_despesa_2020_role_conferido,
                                                                      rateio_despesa_2020_role_nao_conferido,
                                                                      rateio_despesa_2020_ptrf_conferido,
                                                                      rateio_despesa_2020_role_cheque_conferido,
                                                                      periodo_2020_1,
                                                                      conta_associacao_cartao
                                                                      ):
    transacoes_esperadas = [
        {
            'mestre': despesa_2019_2,
            'rateios': [
                rateio_despesa_2019_role_nao_conferido,
                rateio_despesa_2019_role_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 200.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 200.0
                },
            ],
        },
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_nao_conferido,
                rateio_despesa_2020_role_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 300.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 300.0
                },
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
        },

    ]

    conta_uuid = conta_associacao_cartao.uuid

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=False'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_deve_filtrar_transacoes_por_acao(jwt_authenticated_client_a,
                                          acao_associacao_role_cultural,
                                          acao_associacao_ptrf,
                                          despesa_2019_2,
                                          rateio_despesa_2019_role_conferido,
                                          rateio_despesa_2019_role_nao_conferido,
                                          despesa_2020_1,
                                          rateio_despesa_2020_role_conferido,
                                          rateio_despesa_2020_role_nao_conferido,
                                          rateio_despesa_2020_ptrf_nao_conferido,
                                          rateio_despesa_2020_role_cheque_conferido,
                                          periodo_2020_1,
                                          conta_associacao_cartao,
                                          receita_2020_1_ptrf_repasse_nao_conferida,
                                          receita_2020_1_role_outras_nao_conferida,
                                          ):
    """
    Deve retornar apenas receitas da ação filtrada, ou despesas que tenham ao meno sum rateio na ação filtrada
    considerando também o filtro de período, conta e conferido.
    """
    transacoes_esperadas = [
        {
            'mestre': receita_2020_1_ptrf_repasse_nao_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
        },
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_ptrf_nao_conferido,
                rateio_despesa_2020_role_nao_conferido,
                rateio_despesa_2020_role_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 300.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 300.0
                },
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
        },

    ]

    conta_uuid = conta_associacao_cartao.uuid
    acao_uuid = acao_associacao_ptrf.uuid

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=False'

    url = f'{url}&acao_associacao={acao_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_deve_poder_filtrar_tipo_transacao_credito(jwt_authenticated_client_a,
                                                   despesa_2020_1,
                                                   rateio_despesa_2020_role_conferido,
                                                   rateio_despesa_2020_ptrf_conferido,
                                                   rateio_despesa_2020_role_cheque_conferido,
                                                   periodo_2020_1,
                                                   conta_associacao_cartao,
                                                   receita_2020_1_ptrf_repasse_conferida,
                                                   ):
    """
    Deve retornar apenas as receitas se for passado o parâmetro tipo=CREDITOS
    """

    conta_uuid = conta_associacao_cartao.uuid

    transacoes_esperadas = [
        {
            'mestre': receita_2020_1_ptrf_repasse_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
        },

    ]

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=True'

    url = f'{url}&tipo=CREDITOS'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_deve_poder_filtrar_tipo_transacao_gasto(jwt_authenticated_client_a,
                                                 despesa_2020_1,
                                                 rateio_despesa_2020_role_conferido,
                                                 rateio_despesa_2020_ptrf_conferido,
                                                 rateio_despesa_2020_role_cheque_conferido,
                                                 periodo_2020_1,
                                                 conta_associacao_cartao,
                                                 receita_2020_1_ptrf_repasse_conferida,
                                                 ):
    """
    Deve retornar apenas as despesas se for passado o parâmetro tipo=GASTOS
    """

    conta_uuid = conta_associacao_cartao.uuid

    transacoes_esperadas = [
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_conferido,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 200.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 200.0
                },
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
        },

    ]

    result_esperado = monta_result_esperado(transacoes_esperadas=transacoes_esperadas, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=True'

    url = f'{url}&tipo=GASTOS'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de transações esperada."


def test_deve_validar_tipo_transacao(jwt_authenticated_client_a,
                                     despesa_2020_1,
                                     rateio_despesa_2020_role_conferido,
                                     rateio_despesa_2020_ptrf_conferido,
                                     rateio_despesa_2020_role_cheque_conferido,
                                     periodo_2020_1,
                                     conta_associacao_cartao,
                                     receita_2020_1_ptrf_repasse_conferida,
                                     ):
    """
    Deve retornar erro se o tipo informado for diferente de GASTOS e CREDITOS.
    """

    conta_uuid = conta_associacao_cartao.uuid

    result_esperado = {
        'erro': 'parametro_inválido',
        'mensagem': 'O parâmetro tipo pode receber como valor "CREDITOS" ou "GASTOS". '
                    'O parâmetro é opcional.'
    }

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=True'

    url = f'{url}&tipo=INVALIDO'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado, "Não retornou o erro esperado."


def test_deve_validar_conferido(jwt_authenticated_client_a,
                                despesa_2020_1,
                                rateio_despesa_2020_role_conferido,
                                rateio_despesa_2020_ptrf_conferido,
                                rateio_despesa_2020_role_cheque_conferido,
                                periodo_2020_1,
                                conta_associacao_cartao,
                                receita_2020_1_ptrf_repasse_conferida,
                                ):
    """
    Deve retornar erro se o parâmetro conferido informado for diferente de True e False.
    """

    conta_uuid = conta_associacao_cartao.uuid

    result_esperado = {
        'erro': 'parametro_inválido',
        'mensagem': 'O parâmetro "conferido" deve receber como valor "True" ou "False". '
                    'O parâmetro é obrigatório.'
    }

    url = f'/api/conciliacoes/transacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}&conferido=INVALID'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == result_esperado, "Não retornou o erro esperado."
