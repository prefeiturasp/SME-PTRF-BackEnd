import pytest

pytestmark = pytest.mark.django_db


def test_tabela_arquivos(jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/arquivos/tabelas/')
    result = response.json()
    resulta_esperado = {
        'status':
            [
                {'id': 'PENDENTE', 'nome': 'Pendente'},
                {'id': 'SUCESSO', 'nome': 'Sucesso'},
                {'id': 'ERRO', 'nome': 'Erro'},
                {'id': 'PROCESSADO_COM_ERRO', 'nome': 'Processado com erro'}
            ],
        'tipos_cargas':
            [
                {'id': 'REPASSE_REALIZADO', 'nome': 'Repasses realizados'},
                {'id': 'CARGA_PERIODO_INICIAL', 'nome': 'Carga período inicial'},
                {'id': 'REPASSE_PREVISTO', 'nome': 'Repasses previstos'},
                {'id': 'CARGA_ASSOCIACOES', 'nome': 'Carga de Associações'},
                {'id': 'CARGA_USUARIOS', 'nome': 'Carga de usuários'},
                {'id': 'CARGA_CENSO', 'nome': 'Carga de censo'},
                {'id': 'CARGA_REPASSE_PREVISTO_SME', 'nome': 'Repasses previstos sme'}
            ],
        'tipos_delimitadores':
            [
                {'id': 'DELIMITADOR_PONTO_VIRGULA', 'nome': 'Delimitador ponto e vírgula'},
                {'id': 'DELIMITADOR_VIRGULA', 'nome': 'Delimitador vírgula'}
            ]
    }
    return result == resulta_esperado
