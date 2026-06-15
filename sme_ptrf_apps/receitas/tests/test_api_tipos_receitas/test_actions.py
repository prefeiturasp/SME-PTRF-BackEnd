import json
import uuid

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_lista_filtro_por_recurso_uuid(jwt_authenticated_client_p, tipo_receita_estorno, recurso_legado):
    response = jwt_authenticated_client_p.get(
        f'/api/tipos-receitas/?recurso_uuid={recurso_legado.uuid}',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['count'] >= 1


def test_get_filtros_com_recurso_uuid(jwt_authenticated_client_sme, detalhe_tipo_receita, recurso_legado):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/filtros/?recurso_uuid={recurso_legado.uuid}',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'tipos_contas' in content
    assert 'tipos' in content
    assert 'aceita' in content
    assert 'detalhes' in content


def test_get_filtros_recurso_uuid_invalido(jwt_authenticated_client_sme):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/filtros/?recurso_uuid={uuid.uuid4()}',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert content == {'mensagem': 'Recurso não encontrado.'}


def test_unidades_vinculadas_retorna_lista(jwt_authenticated_client_sme, tipo_receita_estorno, unidade, dre_ipiranga):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-vinculadas/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in content


def test_unidades_vinculadas_filtro_por_dre(jwt_authenticated_client_sme, tipo_receita_estorno, dre, dre_ipiranga):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-vinculadas/?dre={dre.uuid}',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_unidades_vinculadas_filtro_por_tipo_unidade(jwt_authenticated_client_sme, tipo_receita_estorno):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-vinculadas/?tipo_unidade=EMEF',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_unidades_vinculadas_filtro_por_nome_ou_codigo(jwt_authenticated_client_sme, tipo_receita_estorno, unidade):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-vinculadas/?nome_ou_codigo=Escola',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_unidades_nao_vinculadas_retorna_lista(jwt_authenticated_client_sme, tipo_receita_estorno, outra_unidade):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-nao-vinculadas/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'results' in content


def test_unidades_nao_vinculadas_filtro_por_dre(jwt_authenticated_client_sme, tipo_receita_estorno, dre):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-nao-vinculadas/?dre={dre.uuid}',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_unidades_nao_vinculadas_filtro_por_tipo_unidade(jwt_authenticated_client_sme, tipo_receita_estorno):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-nao-vinculadas/?tipo_unidade=CEU',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_unidades_nao_vinculadas_filtro_por_nome_ou_codigo(jwt_authenticated_client_sme, tipo_receita_estorno):
    response = jwt_authenticated_client_sme.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidades-nao-vinculadas/?nome_ou_codigo=108600',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_200_OK


def test_vincular_unidade_sucesso(jwt_authenticated_client_sme, tipo_receita_estorno, outra_unidade):
    tipo_receita_estorno.unidades.remove(outra_unidade)

    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidade/{outra_unidade.uuid}/vincular/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'vinculada com sucesso' in content['mensagem']
    assert tipo_receita_estorno.unidades.filter(uuid=outra_unidade.uuid).exists()


def test_vincular_unidade_uuid_invalido(jwt_authenticated_client_sme, tipo_receita_estorno):
    unidade_uuid_invalido = uuid.uuid4()

    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidade/{unidade_uuid_invalido}/vincular/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_vincular_em_lote_sucesso(jwt_authenticated_client_sme, tipo_receita_estorno, outra_unidade):
    tipo_receita_estorno.unidades.remove(outra_unidade)

    payload = {'unidade_uuids': [str(outra_unidade.uuid)]}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/vincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'vinculad' in content['mensagem']


def test_vincular_em_lote_lista_vazia(jwt_authenticated_client_sme, tipo_receita_estorno):
    payload = {'unidade_uuids': []}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/vincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_vincular_em_lote_uuid_nao_encontrado(jwt_authenticated_client_sme, tipo_receita_estorno):
    payload = {'unidade_uuids': [str(uuid.uuid4())]}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/vincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_desvincular_unidade_sucesso(jwt_authenticated_client_sme, tipo_receita_estorno, outra_unidade):
    tipo_receita_estorno.unidades.add(outra_unidade)

    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidade/{outra_unidade.uuid}/desvincular/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'sucesso' in content


def test_desvincular_unidade_nao_encontrada(jwt_authenticated_client_sme, tipo_receita_estorno):
    unidade_uuid_invalido = uuid.uuid4()

    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/unidade/{unidade_uuid_invalido}/desvincular/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_desvincular_em_lote_sucesso(jwt_authenticated_client_sme, tipo_receita_estorno, outra_unidade):
    tipo_receita_estorno.unidades.add(outra_unidade)

    payload = {'unidade_uuids': [str(outra_unidade.uuid)]}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/desvincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['sucesso'] is True


def test_desvincular_em_lote_lista_vazia(jwt_authenticated_client_sme, tipo_receita_estorno):
    payload = {'unidade_uuids': []}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/desvincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_desvincular_em_lote_com_receita_associada(
    jwt_authenticated_client_sme,
    tipo_receita_estorno,
    unidade,
    associacao,
    conta_associacao,
    acao_associacao,
):
    import datetime
    baker.make(
        'Receita',
        tipo_receita=tipo_receita_estorno,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        data=datetime.date(2020, 1, 1),
        valor=100,
    )

    payload = {'unidade_uuids': [str(unidade.uuid)]}
    response = jwt_authenticated_client_sme.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/desvincular-em-lote/',
        content_type='application/json',
        data=json.dumps(payload),
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'mensagem' in content


def test_vincular_todas_unidades_sem_vinculos(jwt_authenticated_client_p, tipo_receita_factory):
    tipo_receita = tipo_receita_factory.create(nome='Tipo Sem Vinculos')

    response = jwt_authenticated_client_p.post(
        f'/api/tipos-receitas/{tipo_receita.uuid}/vincular-todas-unidades/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['sucesso'] is True
    assert 'habilitadas' in content['mensagem']


def test_vincular_todas_unidades_com_vinculos(jwt_authenticated_client_p, tipo_receita_estorno, unidade):
    response = jwt_authenticated_client_p.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/vincular-todas-unidades/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['sucesso'] is True
    assert tipo_receita_estorno.unidades.count() == 0


def test_desvincular_todas_unidades_sem_receitas(jwt_authenticated_client_p, tipo_receita_estorno, unidade):
    response = jwt_authenticated_client_p.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/desvincular-todas-unidades/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['sucesso'] is True
    assert 'desvinculadas' in content['mensagem']
    assert tipo_receita_estorno.unidades.count() == 0


def test_desvincular_todas_unidades_mantem_unidades_com_receita(
    jwt_authenticated_client_p,
    tipo_receita_estorno,
    unidade,
    associacao,
    conta_associacao,
    acao_associacao,
    outra_unidade,
):
    import datetime
    baker.make(
        'Receita',
        tipo_receita=tipo_receita_estorno,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        data=datetime.date(2020, 1, 1),
        valor=100,
    )
    tipo_receita_estorno.unidades.add(outra_unidade)

    response = jwt_authenticated_client_p.post(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/desvincular-todas-unidades/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['sucesso'] is True
    # Unidades com receitas devem permanecer vinculadas
    assert tipo_receita_estorno.unidades.filter(uuid=unidade.uuid).exists()
    # Unidades sem receitas devem ser desvinculadas
    assert not tipo_receita_estorno.unidades.filter(uuid=outra_unidade.uuid).exists()
