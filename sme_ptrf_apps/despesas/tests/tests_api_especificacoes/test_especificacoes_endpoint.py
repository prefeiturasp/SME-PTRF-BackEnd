import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_endpoint(jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/especificacoes/')
    assert response.status_code == status.HTTP_200_OK


def test_listagem_especificacoes(jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/especificacoes-materiais-servicos/')
    assert response.status_code == status.HTTP_200_OK


def test_especificacoes_tabelas(jwt_authenticated_client):

    response = jwt_authenticated_client.get('/api/especificacoes-materiais-servicos/tabelas/')

    assert response.status_code == status.HTTP_200_OK
    assert 'tipos_custeio' in response.data
    assert 'aplicacao_recursos' in response.data


def test_filtros_especificacoes(
        jwt_authenticated_client,
        especificacao_material_servico,
        tipo_custeio):
    params = {
        'ativa': '1',
        'descricao': 'Material',
        'aplicacao_recurso': 'CUSTEIO',
        'tipo_custeio': tipo_custeio.uuid
    }
    response = jwt_authenticated_client.get('/api/especificacoes-materiais-servicos/', params)

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('count') == 1


def test_cadastro_duplicado_especificacao(
        jwt_authenticated_client,
        especificacao_material_servico,
        tipo_custeio):

    payload = {
        'descricao': especificacao_material_servico.descricao,
        'aplicacao_recurso': especificacao_material_servico.aplicacao_recurso,
        'tipo_custeio': tipo_custeio.id
    }

    response = jwt_authenticated_client.post('/api/especificacoes-materiais-servicos/', payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data
    assert 'mensagem' in response.data
    assert response.data['erro'] == 'Duplicated'
    assert response.data['mensagem'] == 'Esta especificação de material e serviço já existe.'


def test_cadastro_com_sucesso(jwt_authenticated_client, tipo_custeio):
    payload = {
        'descricao': 'Especificação Teste',
        'aplicacao_recurso': 'CUSTEIO',
        'tipo_custeio': tipo_custeio.id
    }

    response = jwt_authenticated_client.post('/api/especificacoes-materiais-servicos/', payload)
    assert response.status_code == status.HTTP_201_CREATED


def test_obtencao_especificacao(jwt_authenticated_client, especificacao_material_servico):
    response = jwt_authenticated_client.get(
        f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/')

    assert response.status_code == status.HTTP_200_OK


def test_alteracao_especificacao(jwt_authenticated_client, especificacao_material_servico):
    data = {"descricao": "Descrição Atualizada"}
    response = jwt_authenticated_client.patch(
        f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/', data, format='json')
    assert response.status_code == status.HTTP_200_OK


def test_alteracao_especificacao_com_despesas_vinculadas_alteracao_aplicacao(
        jwt_authenticated_client,
        especificacao_material_servico,
        rateio_despesa_capital):

    data = {"aplicacao_recurso": "CAPITAL"}
    response = jwt_authenticated_client.patch(
        f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/', data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data
    assert 'mensagem' in response.data
    assert response.data['erro'] == 'Despesas vinculadas'
    assert response.data['mensagem'] == ('Não é possível alterar a aplicação do recurso, ' +
                                         'pois já foi utilizado em despesas.')


def test_exclusao_especificacao(jwt_authenticated_client, especificacao_material_servico):
    url = f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/'
    response = jwt_authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_exclusao_especificacao_despesas_vinculadas(
        jwt_authenticated_client,
        especificacao_material_servico,
        rateio_despesa_capital):
    url = f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/'
    response = jwt_authenticated_client.delete(url, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'erro' in response.data
    assert 'mensagem' in response.data
    assert response.data['erro'] == 'ProtectedError', response.data['erro']
    assert response.data['mensagem'] == ('Essa operação não pode ser realizada. ' +
                                         'Há despesas vinculadas à esta especificação')


def test_alteracao_especificacao_sem_alteracao_aplicacao(jwt_authenticated_client, especificacao_material_servico):

    data = {"descricao": "Teste"}
    response = jwt_authenticated_client.patch(
        f'/api/especificacoes-materiais-servicos/{especificacao_material_servico.uuid}/', data, format='json')

    assert response.status_code == status.HTTP_200_OK
