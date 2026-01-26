import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_acao_associacao(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x
):
    response = jwt_authenticated_client_a.get(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    acao_associacao = acao_associacao_charli_bravo_000086_x

    esperado = {
        'uuid': f'{acao_associacao.uuid}',
        'id': acao_associacao.id,
        'saldos': {
            'saldo_atual_capital': 0.0,
            'saldo_atual_custeio': 0.0,
            'saldo_atual_livre': 0.0
        },
        'associacao': {
            'uuid': f'{acao_associacao.associacao.uuid}',
            'nome': acao_associacao.associacao.nome,
            'data_de_encerramento': None,
            'tooltip_data_encerramento': None,
            'tooltip_encerramento_conta': None,
            'encerrada': False,
            'informacoes': acao_associacao.associacao.tags_de_informacao,
            'status_valores_reprogramados': acao_associacao.associacao.status_valores_reprogramados,
            'unidade': {
                'uuid': f'{acao_associacao.associacao.unidade.uuid}',
                'codigo_eol': acao_associacao.associacao.unidade.codigo_eol,
                'nome_com_tipo': acao_associacao.associacao.unidade.nome_com_tipo,
                'nome_dre': acao_associacao.associacao.unidade.nome_dre
            },
            'cnpj': acao_associacao.associacao.cnpj
        },
        'data_de_encerramento_associacao': None,
        'tooltip_associacao_encerrada': None,
        'acao': {
            'id': acao_associacao.acao.id,
            'uuid': f'{acao_associacao.acao.uuid}',
            'nome': acao_associacao.acao.nome,
            'e_recursos_proprios': acao_associacao.acao.e_recursos_proprios,
            'posicao_nas_pesquisas': 'ZZZZZZZZZZ',
            "aceita_capital": acao_associacao.acao.aceita_capital,
            "aceita_custeio": acao_associacao.acao.aceita_custeio,
            "aceita_livre": acao_associacao.acao.aceita_livre,
            "exibir_paa": True,
            "tem_receitas_previstas_paa_em_elaboracao": False,
            "tem_prioridades_paa_em_elaboracao": False,
            "recurso": f'{acao_associacao.acao.recurso.uuid}'
        },
        'status': acao_associacao.status,
        'criado_em': acao_associacao.criado_em.isoformat("T"),
    }
    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_retrieve_acao_associacao_saldo_atual(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x
):
    response = jwt_authenticated_client_a.get(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/obter-saldo-atual/',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    assert 'saldo_atual_capital' in response.data
    assert 'saldo_atual_custeio' in response.data
    assert 'saldo_atual_livre' in response.data
