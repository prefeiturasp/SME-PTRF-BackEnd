import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def monta_result_esperado(lancamentos_esperados, periodo, conta, inativa=False):
    result_esperado = []

    for lancamento in lancamentos_esperados:

        if inativa:
            lancamento["mestre"].mensagem_inativa = f'Este gasto foi excluído em {lancamento["mestre"].data_e_hora_de_inativacao.strftime("%d/%m/%Y %H:%M:%S")}'

        mestre_esperado = {
            'associacao': f'{lancamento["mestre"].associacao.uuid}',
            'numero_documento': lancamento["mestre"].numero_documento,
            'receitas_saida_do_recurso': None,
            'tipo_documento': {
                'id': lancamento["mestre"].tipo_documento.id,
                'nome': lancamento["mestre"].tipo_documento.nome,
            },
            'tipo_transacao': {
                'id': lancamento["mestre"].tipo_transacao.id,
                'nome': lancamento["mestre"].tipo_transacao.nome,
                'tem_documento': lancamento["mestre"].tipo_transacao.tem_documento,
            },
            'documento_transacao': f'{lancamento["mestre"].documento_transacao}',
            'data_documento': f'{lancamento["mestre"].data_documento}',
            'data_transacao': f'{lancamento["mestre"].data_transacao}',
            'mensagem_inativa': lancamento["mestre"].mensagem_inativa if 'mensagem_inativa' in lancamento["mestre"].__dict__ else None,
            'cpf_cnpj_fornecedor': lancamento["mestre"].cpf_cnpj_fornecedor,
            'nome_fornecedor': lancamento["mestre"].nome_fornecedor,
            'valor_ptrf': lancamento["mestre"].valor_ptrf,
            'valor_total': f'{lancamento["mestre"].valor_total:.2f}',
            'status': lancamento["mestre"].status,
            'conferido': lancamento["mestre"].conferido,
            'uuid': f'{lancamento["mestre"].uuid}',
            'data_e_hora_de_inativacao': lancamento["mestre"].data_e_hora_de_inativacao.isoformat("T") if lancamento["mestre"].data_e_hora_de_inativacao else None,

        } if lancamento["tipo"] == 'Gasto' else {
            'associacao': f'{lancamento["mestre"].associacao.uuid}',
            'acao_associacao': {
                'id': lancamento["mestre"].acao_associacao.id,
                'nome': lancamento["mestre"].acao_associacao.acao.nome,
                'e_recursos_proprios': lancamento["mestre"].acao_associacao.acao.e_recursos_proprios,
                'uuid': f'{lancamento["mestre"].acao_associacao.uuid}',
                'acao': {
                    'id': lancamento["mestre"].acao_associacao.acao.id,
                    'uuid': f'{lancamento["mestre"].acao_associacao.acao.uuid}',
                    'nome': lancamento["mestre"].acao_associacao.acao.nome,
                    'e_recursos_proprios': False,
                    'posicao_nas_pesquisas': lancamento["mestre"].acao_associacao.acao.posicao_nas_pesquisas,
                    'aceita_capital': lancamento["mestre"].acao_associacao.acao.aceita_capital,
                    'aceita_custeio': lancamento["mestre"].acao_associacao.acao.aceita_custeio,
                    'aceita_livre': lancamento["mestre"].acao_associacao.acao.aceita_livre
                }
            },
            'categoria_receita': lancamento["mestre"].categoria_receita,
            'tipo_receita': {'id': lancamento["mestre"].tipo_receita.id, 'nome': lancamento["mestre"].tipo_receita.nome},
            'detalhamento': lancamento["mestre"].detalhamento,
            'data': f'{lancamento["mestre"].data}',
            'valor': f'{lancamento["mestre"].valor:.2f}',
            'conferido': lancamento["mestre"].conferido,
            'notificar_dias_nao_conferido': lancamento["mestre"].notificar_dias_nao_conferido,
            'uuid': f'{lancamento["mestre"].uuid}',
        }

        rateios_esperados = []
        for rateio in lancamento["rateios"]:
            rateio_esperado = {
                "tipo_custeio": {
                    'eh_tributos_e_tarifas': False,
                    'id': rateio.tipo_custeio.id,
                    'nome': rateio.tipo_custeio.nome,
                    'uuid': f"{rateio.tipo_custeio.uuid}"
                },
                "especificacao_material_servico": {
                    "id": rateio.especificacao_material_servico.id,
                    "descricao": rateio.especificacao_material_servico.descricao,
                    "aplicacao_recurso": rateio.aplicacao_recurso,
                    "tipo_custeio": rateio.tipo_custeio.id,
                    "ativa": True,
                },
                "notificar_dias_nao_conferido": rateio.notificar_dias_nao_conferido,
                'estorno': {'categoria_receita': None,
                           'data': None,
                           'detalhe_outros': '',
                           'detalhe_tipo_receita': None,
                           'tipo_receita': {'aceita_capital': False,
                                            'aceita_custeio': False,
                                            'aceita_livre': False,
                                            'e_devolucao': False,
                                            'e_recursos_proprios': False,
                                            'e_repasse': False,
                                            'nome': ''},
                           'valor': None},
                "aplicacao_recurso": rateio.aplicacao_recurso,
                "acao_associacao": {
                    "uuid": f'{rateio.acao_associacao.uuid}',
                    "id": rateio.acao_associacao.id,
                    "nome": rateio.acao_associacao.acao.nome,
                    "e_recursos_proprios": rateio.acao_associacao.acao.e_recursos_proprios,
                    'acao': {
                        'id': rateio.acao_associacao.acao.id,
                        'uuid': f'{rateio.acao_associacao.acao.uuid}',
                        'nome': rateio.acao_associacao.acao.nome,
                        'e_recursos_proprios': False,
                        'posicao_nas_pesquisas': rateio.acao_associacao.acao.posicao_nas_pesquisas,
                        'aceita_capital': rateio.acao_associacao.acao.aceita_capital,
                        'aceita_custeio': rateio.acao_associacao.acao.aceita_custeio,
                        'aceita_livre': rateio.acao_associacao.acao.aceita_livre
                    }
                },
                "conferido": rateio.conferido,
                "valor_rateio": f'{rateio.valor_rateio:.2f}',
                "tag": {
                    'uuid': f'{rateio.tag.uuid}',
                    'status': 'Inativo',
                    'nome': f'{rateio.tag.nome}'
                } if rateio.tag else None,
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
                'data': f'{lancamento["mestre"].data_transacao if lancamento["tipo"] == "Gasto" else lancamento["mestre"].data}',
                'tipo_transacao': lancamento["tipo"],
                'numero_documento': lancamento["mestre"].numero_documento if lancamento["tipo"] == "Gasto" else "",
                'descricao': lancamento["mestre"].nome_fornecedor if lancamento["tipo"] == "Gasto" else lancamento[
                    "mestre"].tipo_receita.nome,
                'despesa_geradora_do_imposto': None,
                'despesas_impostos': None,
                'valor_transacao_total': lancamento["mestre"].valor_total if lancamento["tipo"] == "Gasto" else lancamento[
                    "mestre"].valor,
                'valor_transacao_na_conta': lancamento["valor_transacao_na_conta"],
                'valores_por_conta': lancamento["valores_por_conta"],
                'documento_mestre': mestre_esperado,
                'rateios': rateios_esperados,
                'notificar_dias_nao_conferido': max_notificar_dias_nao_conferido if lancamento["tipo"] == "Gasto" else
                lancamento["mestre"].notificar_dias_nao_conferido,
                'conferido': lancamento["mestre"].conferido,
                'analise_lancamento': {
                    'houve_considerados_corretos_automaticamente': False,
                    'analise_prestacao_conta': f'{lancamento["analise_lancamento"].analise_prestacao_conta.uuid}',
                    'despesa': f'{lancamento["mestre"].uuid}',
                    'id': lancamento["analise_lancamento"].id,
                    'status_realizacao': 'PENDENTE',
                    'receita': None,
                    'resultado': 'AJUSTE',
                    'requer_atualizacao_devolucao_ao_tesouro': True,
                    'devolucao_tesouro_atualizada': False,
                    'requer_atualizacao_lancamento': False,
                    'lancamento_atualizado': False,
                    'requer_exclusao_lancamento': False,
                    'lancamento_excluido': False,
                    'requer_ajustes_externos': False,
                    'requer_esclarecimentos': False,
                    'conciliacao_atualizada': False,
                    'requer_conciliacao_lancamento': False,
                    'requer_desconciliacao_lancamento': False,
                    'solicitacoes_de_ajuste_da_analise_total': 1,
                    'solicitacoes_de_ajuste_da_analise': {
                        'analise_lancamento': f'{lancamento["analise_lancamento"].uuid}',
                        'solicitacoes_acerto_por_categoria': [
                            {
                                'acertos': [
                                    {
                                        'tipo_acerto': {
                                            'ativo': True,
                                            'categoria': 'DEVOLUCAO',
                                            'id': lancamento["solicitacao_ajuste"].tipo_acerto.id,
                                            'nome': 'Devolução',
                                            'uuid': f'{lancamento["solicitacao_ajuste"].tipo_acerto.uuid}'
                                        },
                                        'copiado': False,
                                        'detalhamento': 'teste',
                                        'devolucao_ao_tesouro': {
                                            'data': lancamento[
                                                "data_devolucao"] if "data_devolucao" in lancamento else None,
                                            'despesa': {
                                                'associacao': f'{lancamento["mestre"].associacao.uuid}',
                                                'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                                                'data_documento': '2020-03-10',
                                                'data_transacao': '2020-03-10',
                                                'documento_transacao': '',
                                                'nome_fornecedor': 'Fornecedor '
                                                                   'SA',
                                                'numero_documento': '123456',
                                                'tipo_documento': {
                                                    'id': lancamento["mestre"].tipo_documento.id,
                                                    'nome': 'NFe'
                                                },
                                                'tipo_transacao': {
                                                    'id': lancamento["mestre"].tipo_transacao.id,
                                                    'nome': 'Boleto',
                                                    'tem_documento': False
                                                },
                                                'uuid': f'{lancamento["mestre"].uuid}',
                                                'valor_ptrf': 90.0,
                                                'valor_total': '100.00'
                                            },
                                            'devolucao_total': False,
                                            'motivo': 'teste',
                                            'prestacao_conta': f'{lancamento["analise_lancamento"].analise_prestacao_conta.prestacao_conta.uuid}',
                                            'tipo': {
                                                'id': lancamento["solicitacao_devolucao"].tipo.id,
                                                'nome': 'Devolução '
                                                        'teste',
                                                'uuid': f'{lancamento["solicitacao_devolucao"].tipo.uuid}'
                                            },
                                            'uuid': f'{lancamento["solicitacao_devolucao"].uuid}',
                                            'valor': '100.00',
                                            'visao_criacao': 'DRE',
                                            'uuid_registro_devolucao': None
                                        },
                                        'esclarecimentos': None,
                                        'justificativa': None,
                                        'ordem': 1,
                                        'status_realizacao': 'PENDENTE',
                                        'id': lancamento["solicitacao_ajuste"].id,
                                        'uuid': f'{lancamento["solicitacao_ajuste"].uuid}',
                                    }
                                ],
                                'categoria': 'DEVOLUCAO',
                                'despesa': f'{lancamento["mestre"].uuid}',
                                'devolucao_tesouro_atualizada': False,
                                'requer_atualizacao_devolucao_ao_tesouro': True,
                                'receita': None,
                                'analise_lancamento': f'{lancamento["analise_lancamento"].uuid}',
                                'mensagem_inativa': None,
                            }
                        ],
                    },
                    'tipo_lancamento': 'GASTO',
                    'uuid': f'{lancamento["analise_lancamento"].uuid}'
                } if lancamento["analise_lancamento"] else None,
                'informacoes': [
                                {
                                    'tag_hint': 'Parte da despesa foi paga com recursos '
                                                'próprios ou por mais de uma conta.',
                                    'tag_id': '3',
                                    'tag_nome': 'Parcial'},
                               ],
            }
        )

        if lancamento["mestre"].data_e_hora_de_inativacao:
                result_esperado[0]['informacoes'].append({
                    'tag_hint': 'Este gasto foi excluído em 10/05/2020 '
                                '05:10:10',
                    'tag_id': '6',
                    'tag_nome': 'Excluído'
                })

    return result_esperado


def test_api_list_lancamentos_todos_da_conta(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    periodo_2020_1,
    conta_associacao_cartao,
    analise_prestacao_conta_2020_1_teste_analises,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
    solicitacao_acerto_lancamento_devolucao_teste_analises,
    solicitacao_devolucao_ao_tesouro_teste_analises
):
    conta_uuid = conta_associacao_cartao.uuid
    despesa_2020_1.mesagem_inativa = None
    lancamentos_esperados = [
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_role_conferido,
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_nao_conferido
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 300.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 300.0
                },
            ],
            'analise_lancamento': analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
            'solicitacao_ajuste': solicitacao_acerto_lancamento_devolucao_teste_analises,
            'solicitacao_devolucao': solicitacao_devolucao_ao_tesouro_teste_analises,
        },
    ]

    result_esperado = monta_result_esperado(lancamentos_esperados=lancamentos_esperados, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/lancamentos-com-ajustes/?conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)


    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de lançamentos esperados."


def test_api_list_lancamentos_todos_da_conta_inativa(
    jwt_authenticated_client_a,
    despesa_2020_1_inativa,
    rateio_despesa_2020_role_conferido_inativa,
    rateio_despesa_2020_role_nao_conferido_inativa,
    periodo_2020_1,
    conta_associacao_cartao,
    conta_associacao_cheque,
    analise_prestacao_conta_2020_1_teste_inativa_analises,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_inativa_analises,
    solicitacao_acerto_lancamento_devolucao_teste_inativa_analises,
    solicitacao_devolucao_ao_tesouro_teste_inativa_analises
):
    conta_uuid = conta_associacao_cartao.uuid
    lancamentos_esperados = [
        {
            'mestre': despesa_2020_1_inativa,
            'rateios': [
                rateio_despesa_2020_role_conferido_inativa,
                rateio_despesa_2020_role_nao_conferido_inativa,
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 300.0,
            'valor_transacao_total': 100.0,
            'valores_por_conta': [{
                'conta_associacao__tipo_conta__nome': 'Cartão',
                'valor_rateio__sum': 300.0
            }],
            'analise_lancamento': analise_lancamento_despesa_prestacao_conta_2020_1_teste_inativa_analises,
            'solicitacao_ajuste': solicitacao_acerto_lancamento_devolucao_teste_inativa_analises,
            'solicitacao_devolucao': solicitacao_devolucao_ao_tesouro_teste_inativa_analises,
        },
    ]

    result_esperado = monta_result_esperado(lancamentos_esperados=lancamentos_esperados, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao, inativa=True)

    url = f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_inativa_analises.uuid}/lancamentos-com-ajustes/?conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de lançamentos esperados."


def test_api_list_lancamentos_todos_da_conta_por_tipo_ajuste(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    periodo_2020_1,
    conta_associacao_cartao,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    analise_prestacao_conta_2020_1_teste_analises,
    analise_lancamento_receita_prestacao_conta_2020_1_teste_analises,
    analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
    solicitacao_acerto_lancamento_devolucao_teste_analises,
    solicitacao_acerto_lancamento_basico_tipo_teste_analises,
    tipo_acerto_lancamento_devolucao,
    solicitacao_devolucao_ao_tesouro_teste_analises
):
    conta_uuid = conta_associacao_cartao.uuid
    lancamentos_esperados = [
        {
            'mestre': despesa_2020_1,
            'rateios': [
                rateio_despesa_2020_role_conferido,
                rateio_despesa_2020_ptrf_conferido,
                rateio_despesa_2020_role_nao_conferido
            ],
            'tipo': 'Gasto',
            'valor_transacao_na_conta': 300.0,
            'valores_por_conta': [
                {
                    'conta_associacao__tipo_conta__nome': 'Cartão',
                    'valor_rateio__sum': 300.0
                },
            ],
            'analise_lancamento': analise_lancamento_despesa_prestacao_conta_2020_1_teste_analises,
            'solicitacao_ajuste': solicitacao_acerto_lancamento_devolucao_teste_analises,
            'solicitacao_devolucao': solicitacao_devolucao_ao_tesouro_teste_analises,
        },
    ]

    result_esperado = monta_result_esperado(lancamentos_esperados=lancamentos_esperados, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/analises-prestacoes-contas/{analise_prestacao_conta_2020_1_teste_analises.uuid}/lancamentos-com-ajustes/?conta_associacao={conta_uuid}&tipo_acerto={tipo_acerto_lancamento_devolucao.uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de lançamentos esperados."
