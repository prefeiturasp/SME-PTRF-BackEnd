import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def monta_result_esperado(lancamentos_esperados, periodo, conta):
    result_esperado = []

    for lancamento in lancamentos_esperados:

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
            'cpf_cnpj_fornecedor': lancamento["mestre"].cpf_cnpj_fornecedor,
            'nome_fornecedor': lancamento["mestre"].nome_fornecedor,
            'valor_ptrf': lancamento["mestre"].valor_ptrf,
            'valor_total': f'{lancamento["mestre"].valor_total:.2f}',
            'status': lancamento["mestre"].status,
            'conferido': lancamento["mestre"].conferido,
            'uuid': f'{lancamento["mestre"].uuid}',

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
                    'uuid': f'{lancamento["analise_lancamento"].uuid}',
                    'resultado': lancamento["analise_lancamento"].resultado,
                } if lancamento["analise_lancamento"] else None
            }
        )

    return result_esperado


def test_api_get_lancamentos_todos_da_conta(
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
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
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
                {
                    'conta_associacao__tipo_conta__nome': 'Cheque',
                    'valor_rateio__sum': 100.0
                }
            ],
            'analise_lancamento': analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
        },
        {
            'mestre': receita_2020_1_ptrf_repasse_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
            'analise_lancamento': analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
        },
        {
            'mestre': receita_2020_1_role_outras_nao_conferida,
            'rateios': [],
            'tipo': 'Crédito',
            'valor_transacao_na_conta': 100.0,
            'valores_por_conta': [],
            'analise_lancamento': None
        },
    ]

    result_esperado = monta_result_esperado(lancamentos_esperados=lancamentos_esperados, periodo=periodo_2020_1,
                                            conta=conta_associacao_cartao)

    url = f'/api/prestacoes-contas/{prestacao_conta_2020_1_em_analise.uuid}/lancamentos/?analise_prestacao={analise_prestacao_conta_2020_1_em_analise.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == result_esperado, "Não retornou a lista de lancamentos esperados."
