import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_valores_reprogramados_filtro_nome_unidade(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}&search=Duar', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_2.tags_de_informacao,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_cartao': 0,
            'total_conta_cheque': 300.0
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_valores_reprogramados_filtro_nome_associacao(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}&search=Anton', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_2.tags_de_informacao,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_cartao': 0,
            'total_conta_cheque': 300.0
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_valores_reprogramados_filtro_codigo_eol(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}&search=123457', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_2.tags_de_informacao,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_cartao': 0,
            'total_conta_cheque': 300.0
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_valores_reprogramados_filtro_tipo_unidade(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}&tipo_unidade=EMEF', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'data_de_encerramento': None,
                'tooltip_data_encerramento': None,
                'encerrada': False,
                'informacoes': associacao_2.tags_de_informacao,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_cartao': 0,
            'total_conta_cheque': 300.0
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_valores_reprogramados_filtro_status(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    periodo_anterior,
    fechamento_conta_cheque_valores_reprogramados,
    fechamento_conta_cheque_valores_reprogramados_2,
    parametros_dre_valores_reprogramados
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/?dre_uuid={dre.uuid}&status=VALORES_CORRETOS', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

# Endpoint lista associacoes


def test_api_valores_reprogramados_lista_associacoes_filtro_nome_unidade(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    associacao_3,
    periodo_anterior,
    parametros_dre_valores_reprogramados,
    valores_reprogramados_valores_corretos,
    conta_associacao
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/lista-associacoes/?dre_uuid={dre.uuid}&search=Duar', content_type='application/json')
    result = json.loads(response.content)

    # Associacao 3 não entrará na lista pois não possui periodo inicial
    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_um': 0.1,
            'total_conta_dois': '-'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result["valores_reprogramados"] == resultado_esperado


def test_api_valores_reprogramados_lista_associacoes_filtro_nome_associacao(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    associacao_3,
    periodo_anterior,
    parametros_dre_valores_reprogramados,
    valores_reprogramados_valores_corretos,
    conta_associacao
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/lista-associacoes/?dre_uuid={dre.uuid}&search=Anton', content_type='application/json')
    result = json.loads(response.content)

    # Associacao 3 não entrará na lista pois não possui periodo inicial
    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_um': 0.1,
            'total_conta_dois': "-"
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result["valores_reprogramados"] == resultado_esperado


def test_api_valores_reprogramados_lista_associacoes_filtro_codigo_eol(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    associacao_3,
    periodo_anterior,
    parametros_dre_valores_reprogramados,
    valores_reprogramados_valores_corretos,
    conta_associacao
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/lista-associacoes/?dre_uuid={dre.uuid}&search=123457', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_um': 0.1,
            'total_conta_dois': "-"
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result["valores_reprogramados"] == resultado_esperado


def test_api_valores_reprogramados_lista_associacoes_filtro_tipo_unidade(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    associacao_3,
    periodo_anterior,
    parametros_dre_valores_reprogramados,
    valores_reprogramados_valores_corretos,
    conta_associacao
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/lista-associacoes/?dre_uuid={dre.uuid}&tipo_unidade=EMEF', content_type='application/json')
    result = json.loads(response.content)

    # Associacao 3 não entrará na lista pois não possui periodo inicial
    resultado_esperado = [
        {
            'associacao': {
                'cnpj': associacao_2.cnpj,
                'nome': associacao_2.nome,
                'status_valores_reprogramados': associacao_2.status_valores_reprogramados,
                'unidade': {
                    'codigo_eol': unidade_valores_reprogramados.codigo_eol,
                    'nome_com_tipo': unidade_valores_reprogramados.nome_com_tipo,
                    'nome_dre': unidade_valores_reprogramados.nome_dre,
                    'uuid': f'{unidade_valores_reprogramados.uuid}'
                },
                'uuid': f'{associacao_2.uuid}',
            },
            'periodo': {
                'data_fim_realizacao_despesas': f'{periodo_anterior.data_fim_realizacao_despesas}',
                'data_inicio_realizacao_despesas': f'{periodo_anterior.data_inicio_realizacao_despesas}',
                'referencia': periodo_anterior.referencia,
                'referencia_por_extenso': periodo_anterior.referencia_por_extenso,
                'uuid': f'{periodo_anterior.uuid}'
            },
            'total_conta_um': 0.1,
            'total_conta_dois': "-"
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result["valores_reprogramados"] == resultado_esperado


def test_api_valores_reprogramados_lista_associacoes_filtro_status(
    jwt_authenticated_client_dre,
    dre,
    unidade,
    unidade_valores_reprogramados,
    associacao,
    associacao_2,
    associacao_3,
    periodo_anterior,
    parametros_dre_valores_reprogramados,
    valores_reprogramados_valores_corretos,
    conta_associacao
):
    response = jwt_authenticated_client_dre.get(
        f'/api/valores-reprogramados/lista-associacoes/?dre_uuid={dre.uuid}&status=VALORES_CORRETOS', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK

    # Associacao 3 não entrará na lista pois não possui periodo inicial
    assert len(result["valores_reprogramados"]) == 2
