import pytest
import uuid
from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from ...models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.core.fixtures.factories import FlagFactory, UnidadeFactory
from sme_ptrf_apps.paa.fixtures.factories import OutroRecursoPeriodoFactory

BASE_URL = reverse("api:outros-recursos-periodos-paa-list")


@pytest.fixture
def unidade_teste(unidade_factory):
    return unidade_factory.create(
        uuid='f92d2caf-d71f-4ed0-87b2-6d326fb648a6',
        codigo_eol='108500',
        tipo_unidade='EMEF',
        nome='TESTE',
        sigla='TST'
    )


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa, periodo_paa, outro_recurso_factory):
    for index in range(20):
        recurso = outro_recurso_factory.create(nome=f"Outro-Recurso-{index + 1}")
        OutroRecursoPeriodoFactory.create(outro_recurso=recurso, periodo_paa=periodo_paa)

    response = jwt_authenticated_client_sme.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 20
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_outro_recurso_periodo_paa_por_uuid(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["periodo_paa"] == outros_recursos_periodo.periodo_paa.uuid
    assert response.data["outro_recurso"] == outros_recursos_periodo.outro_recurso.uuid
    assert response.data["ativo"] is True


@pytest.mark.django_db
def test_obtem_outro_recurso_periodo_paa_por_periodo_e_recurso(jwt_authenticated_client_sme, outros_recursos_periodo,
                                                               flag_paa):
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    params = {
        "periodo_paa": outros_recursos_periodo.periodo_paa.uuid,
        "outro_recurso": outros_recursos_periodo.outro_recurso.uuid
    }
    response = jwt_authenticated_client_sme.get(url, params)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["periodo_paa"] == outros_recursos_periodo.periodo_paa.uuid
    assert response.data["outro_recurso"] == outros_recursos_periodo.outro_recurso.uuid
    assert response.data["ativo"] is True


@pytest.mark.django_db
def test_cria_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa, periodo_paa, outro_recurso):
    data = {
        "periodo_paa": periodo_paa.uuid,
        "outro_recurso": outro_recurso.uuid,
    }
    response = jwt_authenticated_client_sme.post(BASE_URL, data)

    assert response.status_code == status.HTTP_201_CREATED, response.data
    assert OutroRecursoPeriodoPaa.objects.filter(periodo_paa=periodo_paa, outro_recurso=outro_recurso).exists()


@pytest.mark.django_db
def test_cria_outros_recursos_periodo_duplicado(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    data = {
        "periodo_paa": outros_recursos_periodo.periodo_paa.uuid,
        "outro_recurso": outros_recursos_periodo.outro_recurso.uuid,
    }
    response = jwt_authenticated_client_sme.post(BASE_URL, data)
    result = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'non_field_errors' in result
    assert result["non_field_errors"] == ["Já existe um Recurso cadastrado para o período informado."]


@pytest.mark.django_db
def test_altera_outros_recursos_periodo(jwt_authenticated_client_sme, outros_recursos_periodo, flag_paa):
    assert outros_recursos_periodo.ativo is True
    data = {"ativo": False}
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[outros_recursos_periodo.uuid])
    response = jwt_authenticated_client_sme.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    outros_recursos_periodo.refresh_from_db()
    assert outros_recursos_periodo.ativo is False


@pytest.mark.django_db
def test_exclui_outros_recursos_periodo(jwt_authenticated_client_sme, flag_paa):
    remover = OutroRecursoPeriodoFactory()
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[remover.uuid])
    response = jwt_authenticated_client_sme.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not OutroRecursoPeriodoPaa.objects.filter(uuid=remover.uuid).exists()


@pytest.mark.django_db
def test_exclui_outros_recursos_periodos_inexistente(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de um recurso periodo que não existe"""
    from uuid import uuid4
    uuid_inexistente = uuid4()
    url = reverse("api:outros-recursos-periodos-paa-detail", args=[uuid_inexistente])
    response = jwt_authenticated_client_sme.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_importar_unidades_com_sucesso(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    # Origem com unidades
    unidades = UnidadeFactory.create_batch(3)

    origem = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )
    origem.unidades.add(*unidades)

    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])
    response = jwt_authenticated_client_sme.post(
        url,
        data={"origem_uuid": origem.uuid},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    destino.refresh_from_db()
    assert destino.unidades.count() == 3

    for unidade in unidades:
        assert unidade in destino.unidades.all()


@pytest.mark.django_db
def test_importar_unidades_sem_origem_uuid(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])

    response = jwt_authenticated_client_sme.post(
        url,
        data={},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "origem_uuid é obrigatório."


@pytest.mark.django_db
def test_importar_unidades_origem_inexistente(
    jwt_authenticated_client_sme,
    periodo_paa,
):
    destino = OutroRecursoPeriodoFactory.create(
        periodo_paa=periodo_paa
    )

    url = reverse("api:outros-recursos-periodos-paa-importar-unidades", args=[destino.uuid])

    response = jwt_authenticated_client_sme.post(
        url,
        data={"origem_uuid": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Recurso de origem não encontrado."


@pytest.mark.django_db
def test_vincular_unidade_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste
):
    response_dict = {
        "sucesso": True,
        "mensagem": "Unidade vinculada com sucesso!",
        "unidade": "EMEF XPTO",
        "ja_vinculada": False,
    }

    unidade_uuid = unidade_teste.uuid

    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-unidade",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
            "unidade_uuid": unidade_uuid,
        },
    )
    payload = {
        "confirmado": False,
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 200, response.status_code
    assert response.data["mensagem"] == response_dict['mensagem']


@pytest.mark.django_db
def test_vincular_unidade_ja_vinculada(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste
):
    outros_recursos_periodo.unidades.add(unidade_teste)

    unidade_uuid = unidade_teste.uuid

    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-unidade",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
            "unidade_uuid": unidade_uuid,
        },
    )

    response = jwt_authenticated_client_sme.post(url)

    assert response.status_code == 200, response.status_code
    assert response.data["mensagem"] == "Unidade vinculada com sucesso!", response.data["mensagem"]


@pytest.mark.django_db
def test_vincular_unidade_validacao(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo_inativo,
    unidade_teste
):
    unidade_uuid = unidade_teste.uuid

    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-unidade",
        kwargs={
            "uuid": outros_recursos_periodo_inativo.uuid,
            "unidade_uuid": unidade_uuid,
        },
    )
    payload = {'confirmado': True}

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.data["mensagem"] == "Não é possível vincular unidades a um recurso inativo."


@pytest.mark.django_db
def test_vincular_em_lote_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste
):
    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-em-lote",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
        },
    )

    payload = {
        "unidade_uuids": [unidade_teste.uuid]
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 200
    assert response.data["mensagem"] == "Unidade vinculada com sucesso!"


@pytest.mark.django_db
def test_vincular_em_lote_passando_lista_vazia(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-em-lote",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
        },
    )

    payload = {
        "unidade_uuids": []
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.data["mensagem"] == "Nenhuma unidade foi identificada para vínculo."


@pytest.mark.django_db
def test_vincular_em_lote_passando_uuid_invalido(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    url = reverse(
        "api:outros-recursos-periodos-paa-vincular-em-lote",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
        },
    )

    payload = {
        "unidade_uuids": [uuid.uuid4()]
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.data["mensagem"] == "Nenhuma unidade foi identificada para vínculo."


@pytest.mark.django_db
def test_desvincular_unidade_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste
):
    outros_recursos_periodo.unidades.add(unidade_teste)

    url = reverse(
        "api:outros-recursos-periodos-paa-desvincular-unidade",
        kwargs={
            "uuid": outros_recursos_periodo.uuid,
            "unidade_uuid": unidade_teste.uuid,
        },
    )

    response = jwt_authenticated_client_sme.post(url, format='json')

    assert response.status_code == 200, response.status_code
    assert response.data["mensagem"] == "Unidade desvinculada com sucesso!"


@pytest.mark.django_db
def test_desvincular_unidade_nao_encontrada(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desvinculação quando a unidade não é encontrada"""
    from sme_ptrf_apps.paa.services import UnidadeNaoEncontradaException

    unidade_uuid = uuid.uuid4()

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = UnidadeNaoEncontradaException(
            "Nenhuma unidade foi identificada para desvínculo."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_uuid,
            },
        )

        payload = {'confirmado': True}
        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["mensagem"] == "Nenhuma unidade foi identificada para desvínculo."


@pytest.mark.django_db
def test_desvincular_unidade_validacao_falha(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa desvinculação quando a validação falha"""
    from sme_ptrf_apps.paa.services import ValidacaoVinculoException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = ValidacaoVinculoException(
            "Retorna mensagem de validação"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_teste.uuid,
            },
        )

        payload = {'confirmado': True}
        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Retorna mensagem de validação"


@pytest.mark.django_db
def test_desvincular_unidade_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa erro genérico ao desvincular unidade"""
    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = Exception(
            "Erro genérico"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_teste.uuid,
            },
        )

        payload = {'confirmado': True}
        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro inesperado ao desvincular unidade" in response.data["mensagem"]
        assert str(unidade_teste.uuid) in response.data["mensagem"]


@pytest.mark.django_db
def test_desvincular_unidade_requer_confirmacao(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa desvinculação quando requer confirmação do usuário"""
    from sme_ptrf_apps.paa.services import ConfirmacaoVinculoException as ConfirmException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.validar_confirmacao_para_desvinculo_unidades.side_effect = ConfirmException(
            "Retorna mensagem de confirmação"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_teste.uuid,
            },
        )

        response = jwt_authenticated_client_sme.post(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirmar" in response.data
        assert response.data["confirmar"] == "Retorna mensagem de confirmação"


@pytest.mark.django_db
def test_desvincular_unidade_em_lote_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste
):
    outros_recursos_periodo.unidades.add(unidade_teste)

    url = reverse(
        "api:outros-recursos-periodos-paa-desvincular-em-lote",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    payload = {
        "unidade_uuids": [unidade_teste.uuid]
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 200
    assert response.data["mensagem"] == "Unidade desvinculada com sucesso!"


@pytest.mark.django_db
def test_desvincular_unidade_em_lote_passando_lista_vazia(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    url = reverse(
        "api:outros-recursos-periodos-paa-desvincular-em-lote",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    payload = {
        "unidade_uuids": []
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 400, response.status_code
    assert response.data["mensagem"] == "Nenhuma unidade foi identificada para desvínculo."


@pytest.mark.django_db
def test_desvincular_unidade_inexistente_em_lote(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    url = reverse(
        "api:outros-recursos-periodos-paa-desvincular-em-lote",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    payload = {
        "unidade_uuids": [uuid.uuid4()]
    }

    response = jwt_authenticated_client_sme.post(url, payload, format='json')

    assert response.status_code == 400
    assert response.data["mensagem"] == "Nenhuma unidade foi identificada para desvínculo."


@pytest.mark.django_db
def test_unidades_vinculadas_sem_filtros(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades vinculadas sem filtros"""
    unidades = UnidadeFactory.create_batch(3)
    outros_recursos_periodo.unidades.add(*unidades)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3


@pytest.mark.django_db
def test_unidades_vinculadas_filtro_por_dre(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    dre,
):
    """Testa listagem de unidades vinculadas filtradas por DRE"""
    unidades_dre = UnidadeFactory.create_batch(2, dre=dre)
    unidades_outras_dres = UnidadeFactory.create_batch(2)

    outros_recursos_periodo.unidades.add(*unidades_dre)
    outros_recursos_periodo.unidades.add(*unidades_outras_dres)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"dre": dre.uuid})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_unidades_vinculadas_filtro_por_tipo_unidade(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades vinculadas filtradas por tipo"""
    unidades_emef = UnidadeFactory.create_batch(2, tipo_unidade='EMEF')
    unidades_emei = UnidadeFactory.create_batch(1, tipo_unidade='EMEI')

    outros_recursos_periodo.unidades.add(*unidades_emef)
    outros_recursos_periodo.unidades.add(*unidades_emei)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"tipo_unidade": "EMEF"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_unidades_vinculadas_filtro_por_nome(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades vinculadas filtradas por nome"""
    unidade_teste = UnidadeFactory.create(nome='EMEF TESTE UNIDADE')
    unidade_outra = UnidadeFactory.create(nome='EMEF OUTRA ESCOLA')

    outros_recursos_periodo.unidades.add(unidade_teste, unidade_outra)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"nome_ou_codigo": "TESTE"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_unidades_vinculadas_filtro_por_codigo_eol(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades vinculadas filtradas por código EOL"""
    unidade_teste = UnidadeFactory.create(codigo_eol='234567')
    outros_recursos_periodo.unidades.add(unidade_teste)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"nome_ou_codigo": "234567"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_unidades_nao_vinculadas_sem_filtros(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades não vinculadas sem filtros"""
    unidade_vinculada = UnidadeFactory.create(nome='Vinculada 1')
    unidade_nao_vinculada = UnidadeFactory.create(nome='Não vinculada 1')

    outros_recursos_periodo.unidades.add(unidade_vinculada)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url)
    unidade_nomes = [unidade["nome"] for unidade in response.data["results"]]
    assert response.status_code == status.HTTP_200_OK
    assert unidade_nao_vinculada.nome in unidade_nomes
    assert unidade_vinculada.nome not in unidade_nomes


@pytest.mark.django_db
def test_unidades_nao_vinculadas_filtro_por_dre(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    dre,
):
    """Testa listagem de unidades não vinculadas filtradas por DRE"""
    unidade_vinculada = UnidadeFactory.create(dre=dre)
    UnidadeFactory.create_batch(2, dre=dre)

    outros_recursos_periodo.unidades.add(unidade_vinculada)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"dre": dre.uuid})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 2


@pytest.mark.django_db
def test_unidades_nao_vinculadas_filtro_por_tipo_unidade(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades não vinculadas filtradas por tipo"""
    unidade_vinculada = UnidadeFactory.create(tipo_unidade='EMEF')
    UnidadeFactory.create_batch(2, tipo_unidade='EMEF')
    UnidadeFactory.create_batch(1, tipo_unidade='EMEI')

    outros_recursos_periodo.unidades.add(unidade_vinculada)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"tipo_unidade": "EMEF"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 2


@pytest.mark.django_db
def test_unidades_nao_vinculadas_filtro_por_nome(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades não vinculadas filtradas por nome"""
    unidade_vinculada = UnidadeFactory.create(nome='EMEF VINCULADA')
    UnidadeFactory.create(nome='EMEF TESTE UNIDADE')
    UnidadeFactory.create(nome='EMEF OUTRA ESCOLA')

    outros_recursos_periodo.unidades.add(unidade_vinculada)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"nome_ou_codigo": "TESTE"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_unidades_nao_vinculadas_filtro_por_codigo_eol(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem de unidades não vinculadas filtradas por código EOL"""
    unidade_vinculada = UnidadeFactory.create(codigo_eol='112233')
    UnidadeFactory.create(codigo_eol='445566')
    UnidadeFactory.create(codigo_eol='778899')

    outros_recursos_periodo.unidades.add(unidade_vinculada)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url, {"nome_ou_codigo": "445566"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] >= 1


@pytest.mark.django_db
def test_unidades_nao_vinculadas_todas_vinculadas(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa listagem quando todas as unidades estão vinculadas"""
    from sme_ptrf_apps.core.models.unidade import Unidade

    todas_unidades = list(Unidade.objects.all())
    outros_recursos_periodo.unidades.add(*todas_unidades)

    url = reverse(
        "api:outros-recursos-periodos-paa-unidades-nao-vinculadas",
        kwargs={"uuid": outros_recursos_periodo.uuid},
    )

    response = jwt_authenticated_client_sme.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_vincular_unidade_nao_encontrada(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa vinculação quando a unidade não é encontrada"""
    from sme_ptrf_apps.paa.services import UnidadeNaoEncontradaException

    unidade_uuid = uuid.uuid4()

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset'
            '.OutrosRecursosPeriodoPaaViewSet._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_unidades.side_effect = UnidadeNaoEncontradaException(
            "Unidade não encontrada."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_uuid,
            },
        )

        payload = {'confirmado': True}
        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["mensagem"] == "Unidade não encontrada."


@pytest.mark.django_db
def test_vincular_unidade_requer_confirmacao(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa vinculação quando requer confirmação do usuário"""
    from sme_ptrf_apps.paa.services import ConfirmacaoVinculoException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.validar_confirmacao_para_vinculo_unidades.side_effect = ConfirmacaoVinculoException(
            "Esta unidade já está vinculada a outro recurso ativo. Deseja continuar?"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_teste.uuid,
            },
        )

        response = jwt_authenticated_client_sme.post(url, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirmar" in response.data
        assert response.data["confirmar"] == "Esta unidade já está vinculada a outro recurso ativo. Deseja continuar?"


@pytest.mark.django_db
def test_vincular_unidade_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa vinculação quando ocorre erro genérico não tratado"""
    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_unidades.side_effect = Exception(
            "Erro genérico"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-unidade",
            kwargs={
                "uuid": outros_recursos_periodo.uuid,
                "unidade_uuid": unidade_teste.uuid,
            },
        )

        payload = {'confirmado': True}
        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Erro ao vincular unidade."


@pytest.mark.django_db
def test_vincular_em_lote_unidades_nao_encontradas(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa vinculação em lote quando nenhuma unidade é encontrada"""
    from sme_ptrf_apps.paa.services import UnidadeNaoEncontradaException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_unidades.side_effect = UnidadeNaoEncontradaException(
            "Nenhuma unidade foi identificada para vínculo."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": [uuid.uuid4(), uuid.uuid4()],
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["mensagem"] == "Nenhuma unidade foi identificada para vínculo."


@pytest.mark.django_db
def test_vincular_em_lote_validacao_falha(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
    unidade_teste,
):
    """Testa vinculação em lote quando a validação falha"""
    from sme_ptrf_apps.paa.services import ValidacaoVinculoException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_unidades.side_effect = ValidacaoVinculoException(
            "Não é possível vincular unidades a um recurso inativo."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": [unidade_teste.uuid],
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Não é possível vincular unidades a um recurso inativo."


@pytest.mark.django_db
def test_vincular_em_lote_requer_confirmacao(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa vinculação em lote quando requer confirmação do usuário"""
    from sme_ptrf_apps.paa.services import ConfirmacaoVinculoException

    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.validar_confirmacao_para_vinculo_unidades.side_effect = ConfirmacaoVinculoException(
            "Algumas unidades já estão vinculadas a outros recursos ativos. Deseja continuar?"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirmar" in response.data
        assert response.data["confirmar"] == (
            "Algumas unidades já estão vinculadas a outros recursos ativos. Deseja continuar?")


@pytest.mark.django_db
def test_vincular_em_lote_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa vinculação em lote quando ocorre erro genérico não tratado"""
    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_unidades.side_effect = Exception(
            "Erro Exception"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids,
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Falha ao vincular em lote" in response.data["mensagem"]


@pytest.mark.django_db
def test_desvincular_em_lote_com_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desvinculação em lote com sucesso"""
    unidades_uuids = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]

    resultado_mock = {
        "sucesso": True,
        "mensagem": "Unidades desvinculadas com sucesso!",
        "total_desvinculadas": 3,
        "unidades_removidas": 3
    }

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.return_value = resultado_mock

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids,
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sucesso"] is True
        assert response.data["mensagem"] == "Unidades desvinculadas com sucesso!"
        assert response.data["total_desvinculadas"] == 3
        mock_service.return_value.desvincular_unidades.assert_called_once_with(unidades_uuids)


@pytest.mark.django_db
def test_desvincular_em_lote_unidades_nao_encontradas(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desvinculação em lote quando nenhuma unidade é encontrada"""
    from sme_ptrf_apps.paa.services import UnidadeNaoEncontradaException

    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = UnidadeNaoEncontradaException(
            "Nenhuma unidade foi identificada para desvínculo."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids,
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["mensagem"] == "Nenhuma unidade foi identificada para desvínculo."


@pytest.mark.django_db
def test_desvincular_em_lote_validacao_falha(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desvinculação em lote quando a validação falha"""
    from sme_ptrf_apps.paa.services import ValidacaoVinculoException

    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = ValidacaoVinculoException(
            "Não foi possível desvincular."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids,
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Não foi possível desvincular."


@pytest.mark.django_db
def test_desvincular_em_lote_requer_confirmacao(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desvinculação em lote quando requer confirmação do usuário"""
    from sme_ptrf_apps.paa.services import ConfirmacaoVinculoException as ConfirmException

    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.validar_confirmacao_para_desvinculo_unidades.side_effect = ConfirmException(
            "Algumas unidades possuem PAAs com dados. Deseja continuar?"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirmar" in response.data
        assert response.data["confirmar"] == "Algumas unidades possuem PAAs com dados. Deseja continuar?"


@pytest.mark.django_db
def test_desvincular_em_lote_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa erro genérico ao desvincular em lote"""
    unidades_uuids = [uuid.uuid4(), uuid.uuid4()]

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.desvincular_unidades.side_effect = Exception(
            "Erro de conexão com banco de dados"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desvincular-em-lote",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        payload = {
            "unidade_uuids": unidades_uuids,
            "confirmado": True
        }

        response = jwt_authenticated_client_sme.post(url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Erro ao desvincular em lote"


@pytest.mark.django_db
def test_informacoes_desabilitacao_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa obtenção de informações de desabilitação com sucesso"""
    informacoes_mock = {
        "total_unidades_vinculadas": 5,
        "total_recursos_distribuidos": 3,
        "possui_recursos_finalizados": True,
        "mensagem_confirmacao": "Este recurso possui 5 unidades vinculadas e 3 recursos distribuídos. Deseja continuar?"
    }

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_desabilitacao') as mock_service:
        mock_service.return_value.obter_informacoes_para_confirmacao.return_value = informacoes_mock

        url = reverse(
            "api:outros-recursos-periodos-paa-informacoes-desabilitacao",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_unidades_vinculadas"] == 5
        assert response.data["total_recursos_distribuidos"] == 3
        assert response.data["possui_recursos_finalizados"] is True
        assert "mensagem_confirmacao" in response.data
        mock_service.return_value.obter_informacoes_para_confirmacao.assert_called_once()


@pytest.mark.django_db
def test_informacoes_desabilitacao_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa erro genérico ao obter informações de desabilitação"""
    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_desabilitacao') as mock_service:
        mock_service.return_value.obter_informacoes_para_confirmacao.side_effect = Exception(
            "Erro Genérico"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-informacoes-desabilitacao",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Erro ao obter informações de desabilitação" in response.data["mensagem"]


@pytest.mark.django_db
def test_desabilitar_recurso_com_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa desabilitação de recurso com sucesso"""
    resultado_mock = {
        "sucesso": True,
        "mensagem": "Recurso desabilitado com sucesso.",
        "paas_afetados": 5,
        "receitas_removidas": 3,
        "prioridades_removidas": 2
    }

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_desabilitacao') as mock_service:
        mock_service.return_value.desabilitar_outro_recurso_periodo.return_value = resultado_mock

        url = reverse(
            "api:outros-recursos-periodos-paa-desabilitar",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.patch(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sucesso"] is True
        assert response.data["mensagem"] == "Recurso desabilitado com sucesso."
        assert response.data["paas_afetados"] == 5
        assert response.data["receitas_removidas"] == 3
        assert response.data["prioridades_removidas"] == 2
        mock_service.return_value.desabilitar_outro_recurso_periodo.assert_called_once()


@pytest.mark.django_db
def test_desabilitar_recurso_ja_desabilitado(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo_inativo,
):
    """Testa tentativa de desabilitar recurso já desabilitado"""
    url = reverse(
        "api:outros-recursos-periodos-paa-desabilitar",
        kwargs={"uuid": outros_recursos_periodo_inativo.uuid},
    )

    response = jwt_authenticated_client_sme.patch(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["mensagem"] == "O recurso já está desabilitado."


@pytest.mark.django_db
def test_desabilitar_recurso_desabilitacao_exception(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa erro de desabilitação específico"""
    from sme_ptrf_apps.paa.services import DesabilitacaoRecursoException

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_desabilitacao') as mock_service:
        mock_service.return_value.desabilitar_outro_recurso_periodo.side_effect = DesabilitacaoRecursoException(
            "Não é possível desabilitar recurso com PAAs finalizados."
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desabilitar",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.patch(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Não é possível desabilitar recurso com PAAs finalizados."


@pytest.mark.django_db
def test_desabilitar_recurso_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa erro genérico ao desabilitar recurso"""
    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_desabilitacao') as mock_service:
        mock_service.return_value.desabilitar_outro_recurso_periodo.side_effect = Exception(
            "Erro Exception"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-desabilitar",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.patch(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Erro ao desabilitar outro recurso."


@pytest.mark.django_db
def test_vincular_todas_unidades_com_sucesso(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa vinculação de todas as unidades com sucesso"""
    resultado_mock = {
        "sucesso": True,
        "mensagem": "Todas as unidades foram vinculadas com sucesso!",
        "total_vinculadas": 150,
        "novas_vinculacoes": 145,
        "ja_vinculadas": 5
    }

    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_todas_unidades.return_value = resultado_mock

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-todas-unidades",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["sucesso"] is True
        assert response.data["mensagem"] == "Todas as unidades foram vinculadas com sucesso!"
        assert response.data["total_vinculadas"] == 150
        assert response.data["novas_vinculacoes"] == 145
        assert response.data["ja_vinculadas"] == 5
        mock_service.return_value.vincular_todas_unidades.assert_called_once()


@pytest.mark.django_db
def test_vincular_todas_unidades_erro_generico(
    jwt_authenticated_client_sme,
    flag_paa,
    outros_recursos_periodo,
):
    """Testa erro genérico ao vincular todas as unidades"""
    with patch(
            'sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset.OutrosRecursosPeriodoPaaViewSet'
            '._get_service_vinculo_unidade') as mock_service:
        mock_service.return_value.vincular_todas_unidades.side_effect = Exception(
            "Erro Exception"
        )

        url = reverse(
            "api:outros-recursos-periodos-paa-vincular-todas-unidades",
            kwargs={"uuid": outros_recursos_periodo.uuid},
        )

        response = jwt_authenticated_client_sme.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["mensagem"] == "Erro ao vincular todas as unidades."


@pytest.mark.django_db
def test_get_service_desabilitacao_retorna_instancia_correta(
    outros_recursos_periodo,
):
    """Testa que _get_service_desabilitacao retorna instância do service correta"""
    from sme_ptrf_apps.paa.api.views.outros_recursos_periodo_paa_viewset import OutrosRecursosPeriodoPaaViewSet
    from sme_ptrf_apps.paa.services import OutroRecursoPeriodoDesabilitacaoService

    viewset = OutrosRecursosPeriodoPaaViewSet()
    viewset.kwargs = {'uuid': outros_recursos_periodo.uuid}

    # Mock do get_object para retornar nossa instância
    with patch.object(viewset, 'get_object', return_value=outros_recursos_periodo):
        service = viewset._get_service_desabilitacao()

        assert isinstance(service, OutroRecursoPeriodoDesabilitacaoService)
        assert service.outro_recurso_periodo == outros_recursos_periodo
