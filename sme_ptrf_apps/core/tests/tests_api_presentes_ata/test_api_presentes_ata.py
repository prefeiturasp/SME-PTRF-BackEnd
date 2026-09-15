import json
from unittest.mock import MagicMock, Mock, patch

import pytest
from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


def test_get_presentes_ata_nao_agrupados(
    jwt_authenticated_client_a,
    presente_ata_membro_arnaldo,
    presente_ata_membro_e_conselho_fiscal_benedito,
    presente_ata_nao_membro_carlos
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/?ata__uuid={presente_ata_membro_arnaldo.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 3


def test_get_presentes_agrupados(
    jwt_authenticated_client_a,
    presente_ata_membro,
    presente_ata_membro_e_conselho_fiscal,
    presente_ata_nao_membro,
    membro_associacao_presidente_conselho_01
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['presentes_ata_conselho_fiscal']) == 1
    assert len(result['presentes_membros']) == 2
    assert len(result['presentes_nao_membros']) == 1


def test_get_padrao_presentes(
    jwt_authenticated_client_a, presente_ata_membro,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/padrao-de-presentes/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_nome_cargo_membro_associacao(jwt_authenticated_client_a, presente_ata_membro):
    identificador = "12345"
    url = (
        '/api/presentes-ata/get-nome-cargo-membro-associacao/'
        f'?ata_uuid={presente_ata_membro.ata.uuid}&identificador={identificador}'
    )
    response = jwt_authenticated_client_a.get(url, content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_get_presentes_agrupados_sem_ata_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/membros-e-nao-membros/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_get_presentes_agrupados_ata_nao_encontrada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/membros-e-nao-membros/?ata_uuid=uuid-invalido', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_get_presentes_agrupados_flag_historico_membros_sem_presentes(
    jwt_authenticated_client_a, ata_2020_1_teste,
):
    with override_flag('historico-de-membros', active=True):
        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={ata_2020_1_teste.uuid}',
            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
        'presentes_membros': [],
        'presentes_nao_membros': [],
        'presentes_ata_conselho_fiscal': []
    }


def test_get_presentes_agrupados_flag_historico_membros_com_presentes(
    jwt_authenticated_client_a,
    presente_ata_membro_arnaldo,
    presente_ata_membro_e_conselho_fiscal_benedito,
    presente_ata_nao_membro_carlos,
):
    with override_flag('historico-de-membros', active=True):
        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={presente_ata_membro_arnaldo.ata.uuid}',
            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['presentes_membros']) == 2
    assert len(result['presentes_nao_membros']) == 1
    assert len(result['presentes_ata_conselho_fiscal']) == 1


def test_get_presentes_agrupados_flag_off_sem_membros_presentes(
    jwt_authenticated_client_a, ata_2020_1_teste, membro_associacao_presidente_valido,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/membros-e-nao-membros/?ata_uuid={ata_2020_1_teste.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['presentes_membros']) == 1
    assert result['presentes_membros'][0]['nome'] == membro_associacao_presidente_valido.nome


def test_get_padrao_presentes_sem_ata_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/padrao-de-presentes/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_get_padrao_presentes_ata_nao_encontrada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/padrao-de-presentes/?ata_uuid=uuid-invalido', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_get_padrao_presentes_com_membros(
    jwt_authenticated_client_a, ata_2020_1_teste, membro_associacao_presidente_valido,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/padrao-de-presentes/?ata_uuid={ata_2020_1_teste.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0]['nome'] == membro_associacao_presidente_valido.nome
    assert result[0]['identificacao'] == membro_associacao_presidente_valido.codigo_identificacao


def test_presentes_padrao_conselho_fiscal(
    jwt_authenticated_client_a, ata_2020_1_teste, membro_associacao_presidente_conselho_01,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/presentes-padrao-conselho-fiscal/?ata_uuid={ata_2020_1_teste.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['presidente_conselho_fiscal']) == 1
    assert result['conselheiro_1'] == []


def test_presentes_padrao_conselho_fiscal_sem_ata_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/presentes-padrao-conselho-fiscal/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_presentes_padrao_conselho_fiscal_ata_nao_encontrada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/presentes-padrao-conselho-fiscal/?ata_uuid=uuid-invalido',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_nome_cargo_membro_associacao_sem_identificador(jwt_authenticated_client_a, presente_ata_membro):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/get-nome-cargo-membro-associacao/?ata_uuid={presente_ata_membro.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_nome_cargo_membro_associacao_sem_ata_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/get-nome-cargo-membro-associacao/?identificador=12345',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'parametros_requeridos'


def test_nome_cargo_membro_associacao_ata_nao_encontrada(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/get-nome-cargo-membro-associacao/?ata_uuid=uuid-invalido&identificador=12345',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'Objeto não encontrado.'


def test_nome_cargo_membro_associacao_flag_off_membro_encontrado(
    jwt_authenticated_client_a, ata_2020_1_teste, membro_associacao_presidente_valido,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/get-nome-cargo-membro-associacao/'
        f'?ata_uuid={ata_2020_1_teste.uuid}&identificador={membro_associacao_presidente_valido.codigo_identificacao}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
        'mensagem': 'membro-encontrado',
        'nome': membro_associacao_presidente_valido.nome,
        'cargo': 'Presidente da Diretoria Executiva',
    }


def test_nome_cargo_membro_associacao_flag_ativa_sem_data(jwt_authenticated_client_a, presente_ata_membro):
    with override_flag('historico-de-membros', active=True):
        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/get-nome-cargo-membro-associacao/'
            f'?ata_uuid={presente_ata_membro.ata.uuid}&identificador=12345',
            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['mensagem'] == 'servidor-nao-encontrado'


def test_nome_cargo_membro_associacao_flag_ativa_ocupante_nao_encontrado(
    jwt_authenticated_client_a, presente_ata_membro,
):
    with override_flag('historico-de-membros', active=True):
        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/get-nome-cargo-membro-associacao/'
            f'?ata_uuid={presente_ata_membro.ata.uuid}&identificador=12345&data=2020-07-01',
            content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['mensagem'] == 'servidor-nao-encontrado'


def test_nome_cargo_membro_associacao_flag_ativa_membro_encontrado_na_composicao(
    jwt_authenticated_client_a, presente_ata_membro, ocupante_cargo_factory,
):
    ocupante = ocupante_cargo_factory(nome='Fulano de Tal', codigo_identificacao='12345')

    mock_composicao = MagicMock()
    mock_composicao.cargos_da_composicao_da_composicao.filter.return_value.exists.return_value = True

    mock_cargo = Mock(cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA')

    path_servico = 'sme_ptrf_apps.core.api.views.presentes_ata_viewset.ServicoRecuperaComposicaoPorData'
    path_cargo_get = 'sme_ptrf_apps.core.api.views.presentes_ata_viewset.CargoComposicao.objects.get'

    with override_flag('historico-de-membros', active=True), \
            patch(path_servico) as MockServico, \
            patch(path_cargo_get, return_value=mock_cargo):
        MockServico.return_value.get_composicao_por_data_e_associacao.return_value = mock_composicao

        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/get-nome-cargo-membro-associacao/'
            f'?ata_uuid={presente_ata_membro.ata.uuid}&identificador=12345&data=2020-07-01',
            content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == {
        'mensagem': 'membro-encontrado',
        'nome': ocupante.nome,
        'cargo': 'Presidente da Diretoria Executiva',
    }


def test_nome_cargo_membro_associacao_flag_ativa_ocupante_fora_da_composicao(
    jwt_authenticated_client_a, presente_ata_membro, ocupante_cargo_factory,
):
    ocupante_cargo_factory(nome='Fulano de Tal', codigo_identificacao='12345')

    mock_composicao = MagicMock()
    mock_composicao.cargos_da_composicao_da_composicao.filter.return_value.exists.return_value = False

    path_servico = 'sme_ptrf_apps.core.api.views.presentes_ata_viewset.ServicoRecuperaComposicaoPorData'

    with override_flag('historico-de-membros', active=True), \
            patch(path_servico) as MockServico:
        MockServico.return_value.get_composicao_por_data_e_associacao.return_value = mock_composicao

        response = jwt_authenticated_client_a.get(
            f'/api/presentes-ata/get-nome-cargo-membro-associacao/'
            f'?ata_uuid={presente_ata_membro.ata.uuid}&identificador=12345&data=2020-07-01',
            content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['mensagem'] == 'servidor-nao-encontrado'


def test_get_participantes_ordenados_por_cargo(
    jwt_authenticated_client_a, presente_ata_membro_arnaldo, presente_ata_nao_membro_carlos,
):
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/get-participantes-ordenados-por-cargo/?ata_uuid={presente_ata_membro_arnaldo.ata.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2
    nomes = [item['nome'] for item in result]
    assert 'Arnaldo' in nomes
    assert 'Carlos' in nomes


def test_get_participantes_ordenados_por_cargo_sem_ata_uuid(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(
        '/api/presentes-ata/get-participantes-ordenados-por-cargo/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['erro'] == 'O parâmetro "ata_uuid" é obrigatório'


def test_get_participantes_ordenados_por_cargo_ata_nao_existe(jwt_authenticated_client_a):
    import uuid
    response = jwt_authenticated_client_a.get(
        f'/api/presentes-ata/get-participantes-ordenados-por-cargo/?ata_uuid={uuid.uuid4()}',
        content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert result['erro'] == 'A ata especificada não existe'
