import pytest
from rest_framework import status
from sme_ptrf_apps.paa.fixtures.factories.receitas_previstas_pdde_factory import ReceitaPrevistaPddeFactory
from ...models import AcaoPdde
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import AcaoPddeFactory
from sme_ptrf_apps.paa.fixtures.factories.periodo_paa import PeriodoPaaFactory
from sme_ptrf_apps.paa.fixtures.factories.paa import (
    PaaFactory)

@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_acao_pdde(jwt_authenticated_client_sme, programa_pdde, flag_paa):

    for index in range(50):
        AcaoPddeFactory.create(nome=f"Ação-pdde-{index + 1}", programa=programa_pdde)

    response = jwt_authenticated_client_sme.get("/api/acoes-pdde/?programa_nome=Categ&nome=Ação")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 50
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]
    assert response.data["links"]['next'] is not None


@pytest.mark.django_db
def test_obtem_acao_pdde(jwt_authenticated_client_sme, acao_pdde, flag_paa):
    response = jwt_authenticated_client_sme.get(f"/api/acoes-pdde/{acao_pdde.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Ação PDDE Teste"


@pytest.mark.django_db
def test_cria_acao_pdde(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"nome": "Nova Ação", "programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert AcaoPdde.objects.filter(nome="Nova Ação").exists()


@pytest.mark.django_db
def test_cria_acao_pdde_sem_nome(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in response.data
    assert response.data["nome"] == "Nome da ação PDDE não foi informado."


@pytest.mark.django_db
def test_cria_acao_pdde_sem_programa(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "novo"}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'programa' in response.data
    assert response.data["programa"] == "O Programa PDDE não foi informado."


@pytest.mark.django_db
def test_cria_acao_pdde_duplicado(jwt_authenticated_client_sme, acao_pdde, programa_pdde, flag_paa):
    data = {"nome": acao_pdde.nome, "programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated"
    assert response.data["detail"] == ("Erro ao criar Ação PDDE. Já existe uma " +
                                       "Ação PDDE cadastrada com este nome e programa.")


@pytest.mark.django_db
def test_atualizar_acao_pdde_duplicado(jwt_authenticated_client_sme, acao_pdde, programa_pdde, flag_paa):
    cadastro = AcaoPddeFactory.create(nome="Novo", programa=programa_pdde)

    data = {"nome": acao_pdde.nome, "programa": programa_pdde.uuid}

    response = jwt_authenticated_client_sme.patch("/api/acoes-pdde/" + str(cadastro.uuid) + "/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated", response.content
    assert response.data["detail"] == ("Erro ao atualizar Ação PDDE. Já existe uma " +
                                       "Ação PDDE cadastrada com este nome e programa.")


@pytest.mark.django_db
def test_altera_acao_pdde(jwt_authenticated_client_sme, acao_pdde, flag_paa):
    data = {"nome": "Novo Nome", "programa": acao_pdde.programa.uuid}
    response = jwt_authenticated_client_sme.patch(f"/api/acoes-pdde/{acao_pdde.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK, response.content
    acao_pdde.refresh_from_db()
    assert acao_pdde.nome == "Novo Nome"


@pytest.mark.django_db
def test_exclui_acao_pdde(jwt_authenticated_client_sme, flag_paa):
    acao = AcaoPddeFactory(nome="Deletar")
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao.uuid}/")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_cria_exclui_e_verifica_status_inativa(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    # 1. Criar uma nova ação PDDE
    data = {"nome": "Ação para Excluir", "programa": programa_pdde.uuid}
    response = jwt_authenticated_client_sme.post("/api/acoes-pdde/", data)
    
    assert response.status_code == status.HTTP_201_CREATED
    acao_uuid = response.data["uuid"]
    
    # Verificar que a ação foi criada com status ATIVA
    acao = AcaoPdde.objects.get(uuid=acao_uuid)
    assert acao.status == AcaoPdde.STATUS_ATIVA
    
    # 2. Excluir a ação PDDE (que na verdade a inativa)
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao_uuid}/")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # 3. Verificar se o status foi alterado para INATIVA ou se o objeto foi excluído
    try:
        acao.refresh_from_db()
        # Se chegou aqui, o objeto ainda existe e foi inativado
        assert acao.status == AcaoPdde.STATUS_INATIVA
    except AcaoPdde.DoesNotExist:
        # Se o objeto foi excluído fisicamente, verificar se não existe mais no banco
        assert not AcaoPdde.objects.filter(uuid=acao_uuid).exists()


@pytest.mark.django_db
def test_destroy_acao_pdde_com_receitas_vinculadas(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de uma ação PDDE que está sendo usada em receitas previstas PDDE"""
    from sme_ptrf_apps.paa.models import PeriodoPaa, Paa, ReceitaPrevistaPdde
    from datetime import date, timedelta
    
    # Criar período vigente
    hoje = date.today()
    periodo_vigente = PeriodoPaaFactory(
        data_inicial=hoje - timedelta(days=30),
        data_final=hoje + timedelta(days=30)
    )
    
    # Criar PAA para o período vigente
    paa_vigente = PaaFactory(periodo_paa=periodo_vigente)
    
    # Criar ação PDDE
    acao_pdde = AcaoPddeFactory()
    
    # Criar receita prevista PDDE vinculada à ação
    ReceitaPrevistaPddeFactory(
        paa=paa_vigente,
        acao_pdde=acao_pdde
    )
    
    # Tentar excluir a ação PDDE
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao_pdde.uuid}/")
    
    # Deve retornar erro 409 (Conflict) porque a ação está sendo usada
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Esta ação PDDE não pode ser excluída porque está sendo utilizada em um Plano Anual de Atividades (PAA)." in response.data["detail"]


@pytest.mark.django_db
def test_destroy_acao_pdde_sem_receitas_vinculadas(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de uma ação PDDE que não está sendo usada em receitas previstas PDDE"""
    from sme_ptrf_apps.paa.models import PeriodoPaa, Paa
    from datetime import date, timedelta
    
    # Criar período vigente
    hoje = date.today()
    periodo_vigente = PeriodoPaaFactory(
        data_inicial=hoje - timedelta(days=30),
        data_final=hoje + timedelta(days=30)
    )
    
    # Criar PAA para o período vigente
    paa_vigente = PaaFactory(periodo_paa=periodo_vigente)
    
    # Criar ação PDDE
    acao_pdde = AcaoPddeFactory()
    
    # Verificar que a ação foi criada com status ATIVA
    assert acao_pdde.status == AcaoPdde.STATUS_ATIVA
    
    # Refresh para garantir que a ação foi criada
    acao_pdde.refresh_from_db()
    
    # Excluir a ação PDDE
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao_pdde.uuid}/")
    
    # Deve retornar sucesso
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar se o status foi alterado para INATIVA ou se o objeto foi excluído
    try:
        acao_pdde.refresh_from_db()
        # Se chegou aqui, o objeto ainda existe e foi inativado
        assert acao_pdde.status == AcaoPdde.STATUS_INATIVA
    except AcaoPdde.DoesNotExist:
        # Se o objeto foi excluído fisicamente, verificar se não existe mais no banco
        assert not AcaoPdde.objects.filter(uuid=acao_pdde.uuid).exists()


@pytest.mark.django_db
def test_destroy_acao_pdde_sem_periodo_vigente(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de uma ação PDDE quando não há período vigente"""
    # Criar ação PDDE
    acao_pdde = AcaoPddeFactory()
    
    # Verificar que a ação foi criada com status ATIVA
    assert acao_pdde.status == AcaoPdde.STATUS_ATIVA
    
    # Excluir a ação PDDE
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{acao_pdde.uuid}/")
    
    # Deve retornar sucesso mesmo sem período vigente
    # O comportamento atual da API retorna 204 quando não há período vigente
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verificar se o status foi alterado para INATIVA ou se o objeto foi excluído
    try:
        acao_pdde.refresh_from_db()
        # Se chegou aqui, o objeto ainda existe e foi inativado
        assert acao_pdde.status == AcaoPdde.STATUS_INATIVA
    except AcaoPdde.DoesNotExist:
        # Se o objeto foi excluído fisicamente, verificar se não existe mais no banco
        assert not AcaoPdde.objects.filter(uuid=acao_pdde.uuid).exists()


@pytest.mark.django_db
def test_destroy_acao_pdde_inexistente(jwt_authenticated_client_sme, flag_paa):
    """Testa a exclusão de uma ação PDDE que não existe"""
    from uuid import uuid4
    
    # Tentar excluir uma ação PDDE com UUID inexistente
    uuid_inexistente = uuid4()
    response = jwt_authenticated_client_sme.delete(f"/api/acoes-pdde/{uuid_inexistente}/")
    print(response.data)
    # Deve retornar erro 404 (Not Found)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Ação PDDE não encontrada." in response.data["detail"]