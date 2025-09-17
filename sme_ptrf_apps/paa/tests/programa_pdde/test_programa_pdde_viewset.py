import pytest
from rest_framework import status

from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.fixtures.factories import ProgramaPddeFactory
from sme_ptrf_apps.paa.models import ProgramaPdde


@pytest.fixture
def flag_paa():
    return FlagFactory.create(name='paa')


@pytest.mark.django_db
def test_lista_programa(jwt_authenticated_client_sme, flag_paa):
    ProgramaPddeFactory(nome="Programa-teste-1")
    ProgramaPddeFactory(nome="Programa-teste-2")
    ProgramaPddeFactory(nome="Programa-teste-3")
    ProgramaPddeFactory(nome="Programa-teste-4")

    response = jwt_authenticated_client_sme.get("/api/programas-pdde/?nome=Programa-teste")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 4
    assert 'links' in response.data
    assert 'next' in response.data["links"]
    assert 'previous' in response.data["links"]


@pytest.mark.django_db
def test_obtem_programa(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    response = jwt_authenticated_client_sme.get(f"/api/programas-pdde/{programa_pdde.uuid}/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Programa PDDE Teste"


@pytest.mark.django_db
def test_cria_programa(jwt_authenticated_client_sme, flag_paa):
    data = {"nome": "Nova Programa"}
    response = jwt_authenticated_client_sme.post("/api/programas-pdde/", data)

    assert response.status_code == status.HTTP_201_CREATED
    assert ProgramaPdde.objects.filter(nome="Nova Programa").exists()


@pytest.mark.django_db
def test_cria_programa_sem_nome(jwt_authenticated_client_sme, flag_paa):
    data = {}
    response = jwt_authenticated_client_sme.post("/api/programas-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'nome' in response.data
    assert response.data["nome"] == "Nome do Programa PDDE não foi informado."


@pytest.mark.django_db
def test_cria_programa_duplicada(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"nome": programa_pdde.nome}
    response = jwt_authenticated_client_sme.post("/api/programas-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated"
    assert response.data["detail"] == ("Erro ao criar Programa PDDE. Já existe um "
                                       "Programa PDDE cadastrado com este nome.")


@pytest.mark.django_db
def test_cria_programa_duplicada_case_sensitive(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"nome": programa_pdde.nome.lower()}
    response = jwt_authenticated_client_sme.post("/api/programas-pdde/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data["erro"] == "Duplicated"
    assert response.data["detail"] == ("Erro ao criar Programa PDDE. Já existe um "
                                       "Programa PDDE cadastrado com este nome.")


@pytest.mark.django_db
def test_altera_programa(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    data = {"nome": "Novo Nome"}
    response = jwt_authenticated_client_sme.patch(f"/api/programas-pdde/{programa_pdde.uuid}/", data)

    assert response.status_code == status.HTTP_200_OK
    programa_pdde.refresh_from_db()
    assert programa_pdde.nome == "Novo Nome"


@pytest.mark.django_db
def test_altera_programa_para_duplicado_existente(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    categoria = ProgramaPddeFactory(nome="Novo Nome")
    data = {"nome": programa_pdde.nome}
    response = jwt_authenticated_client_sme.patch(f"/api/programas-pdde/{categoria.uuid}/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data['erro'] == 'Duplicated'
    assert response.data['detail'] == ("Erro ao atualizar Programa PDDE. Já existe um " +
                                       "Programa PDDE cadastrado com este nome.")


@pytest.mark.django_db
def test_altera_programa_para_duplicado_existente_case_sensitive(jwt_authenticated_client_sme, programa_pdde, flag_paa):
    categoria = ProgramaPddeFactory(nome="Novo Nome")
    data = {"nome": programa_pdde.nome.lower()}
    response = jwt_authenticated_client_sme.patch(f"/api/programas-pdde/{categoria.uuid}/", data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'detail' in response.data
    assert 'erro' in response.data
    assert response.data['erro'] == 'Duplicated'
    assert response.data['detail'] == ("Erro ao atualizar Programa PDDE. Já existe um " +
                                       "Programa PDDE cadastrado com este nome.")


@pytest.mark.django_db
def test_exclui_programa_erro(jwt_authenticated_client_sme, acao_pdde, acao_pdde_2, flag_paa):
    response = jwt_authenticated_client_sme.delete(
        f"/api/programas-pdde/{acao_pdde.programa.uuid}/?acao_pdde_uuid={acao_pdde_2.uuid}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["erro"] == "ProtectedError"
    assert response.data == {
        'erro': 'ProtectedError',
        'mensagem': 'Não é possível excluir. Este programa ainda está vinculado há alguma ação.'
    }


@pytest.mark.django_db
def test_exclui_programa_sem_acao(jwt_authenticated_client_sme, acao_pdde, programa_pdde_3, flag_paa):
    response = jwt_authenticated_client_sme.delete(
        f"/api/programas-pdde/{programa_pdde_3.uuid}/?acao_pdde_uuid={acao_pdde.uuid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ProgramaPdde.objects.filter(uuid=programa_pdde_3.uuid).exists()


@pytest.mark.django_db
def test_obtem_programas_somatorio(jwt_authenticated_client_sme,
                                   flag_paa,
                                   programa_pdde,
                                   programa_pdde_2,
                                   programa_pdde_3,
                                   acao_pdde_factory,
                                   paa,
                                   receita_prevista_pdde_factory
                                   ):
    acao_pdde1 = acao_pdde_factory.create(
        programa=programa_pdde,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde2 = acao_pdde_factory.create(
        programa=programa_pdde_2,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde3 = acao_pdde_factory.create(
        programa=programa_pdde_2,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde4 = acao_pdde_factory.create(
        programa=programa_pdde_3,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde5 = acao_pdde_factory.create(
        programa=programa_pdde_3,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)

    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde1,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde1,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde2,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde3,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde4,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde5,
        saldo_custeio=110.00, saldo_capital=150.00, saldo_livre=200.00,
        previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre=415.00)

    response = jwt_authenticated_client_sme.get(f"/api/programas-pdde/totais/?paa_uuid={paa.uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert 'programas' in response.data
    assert 'total' in response.data
    total_custeios = (6 * 110) + (140 * 6)
    total_capital = (6 * 150) + (312 * 6)
    total_livre = (6 * 200) + (415 * 6)
    assert response.data["total"] == {
        "total_valor_custeio": total_custeios,
        "total_valor_capital": total_capital,
        "total_valor_livre_aplicacao": total_livre,
        "total": total_custeios + total_capital + total_livre
    }
    assert response.data["programas"][0]["nome"] == "Programa PDDE Teste"
    assert response.data["programas"][0]["total_valor_custeio"] == 500.
    assert response.data["programas"][0]["total_valor_capital"] == 924.
    assert response.data["programas"][0]["total_valor_livre_aplicacao"] == 1230.


@pytest.mark.django_db
def test_obtem_programas_somatorio_com_page_size_padrao(jwt_authenticated_client_sme,
                                                        flag_paa,
                                                        programa_pdde,
                                                        programa_pdde_2,
                                                        programa_pdde_3,
                                                        acao_pdde_factory,
                                                        paa,
                                                        receita_prevista_pdde_factory
                                                        ):
    """Testa o comportamento padrão do page_size (1000) quando não informado"""
    acao_pdde1 = acao_pdde_factory.create(
        programa=programa_pdde,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde2 = acao_pdde_factory.create(
        programa=programa_pdde_2,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)

    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde1,
        saldo_custeio=100.00, saldo_capital=200.00, saldo_livre=300.00,
        previsao_valor_custeio=150.00, previsao_valor_capital=250.00, previsao_valor_livre=350.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde2,
        saldo_custeio=50.00, saldo_capital=100.00, saldo_livre=150.00,
        previsao_valor_custeio=75.00, previsao_valor_capital=125.00, previsao_valor_livre=175.00)

    # Testa sem page_size (deve usar padrão 1000)
    response = jwt_authenticated_client_sme.get(f"/api/programas-pdde/totais/?paa_uuid={paa.uuid}")

    assert response.status_code == status.HTTP_200_OK
    assert 'programas' in response.data
    assert 'total' in response.data
    # Verifica se retornou todos os programas (3 programas criados)
    assert len(response.data["programas"]) == 3


@pytest.mark.django_db
def test_obtem_programas_somatorio_com_page_size_customizado(jwt_authenticated_client_sme,
                                                            flag_paa,
                                                            programa_pdde,
                                                            programa_pdde_2,
                                                            programa_pdde_3,
                                                            acao_pdde_factory,
                                                            paa,
                                                            receita_prevista_pdde_factory
                                                            ):
    """Testa o page_size customizado limitando a 2 programas"""
    acao_pdde1 = acao_pdde_factory.create(
        programa=programa_pdde,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde2 = acao_pdde_factory.create(
        programa=programa_pdde_2,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde3 = acao_pdde_factory.create(
        programa=programa_pdde_3,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)

    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde1,
        saldo_custeio=100.00, saldo_capital=200.00, saldo_livre=300.00,
        previsao_valor_custeio=150.00, previsao_valor_capital=250.00, previsao_valor_livre=350.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde2,
        saldo_custeio=50.00, saldo_capital=100.00, saldo_livre=150.00,
        previsao_valor_custeio=75.00, previsao_valor_capital=125.00, previsao_valor_livre=175.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde3,
        saldo_custeio=25.00, saldo_capital=50.00, saldo_livre=75.00,
        previsao_valor_custeio=30.00, previsao_valor_capital=60.00, previsao_valor_livre=90.00)

    # Testa com page_size=2 (deve retornar apenas 2 programas)
    response = jwt_authenticated_client_sme.get(f"/api/programas-pdde/totais/?paa_uuid={paa.uuid}&page_size=2")

    assert response.status_code == status.HTTP_200_OK
    assert 'programas' in response.data
    assert 'total' in response.data
    # Verifica se retornou apenas 2 programas devido ao page_size
    assert len(response.data["programas"]) == 2


@pytest.mark.django_db
def test_obtem_programas_somatorio_com_page_size_invalido(jwt_authenticated_client_sme,
                                                         flag_paa,
                                                         programa_pdde,
                                                         programa_pdde_2,
                                                         programa_pdde_3,
                                                         acao_pdde_factory,
                                                         paa,
                                                         receita_prevista_pdde_factory
                                                         ):
    """Testa o page_size inválido (deve usar padrão 1000)"""
    acao_pdde1 = acao_pdde_factory.create(
        programa=programa_pdde,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)
    acao_pdde2 = acao_pdde_factory.create(
        programa=programa_pdde_2,
        aceita_capital=True,
        aceita_custeio=True,
        aceita_livre_aplicacao=True)

    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde1,
        saldo_custeio=100.00, saldo_capital=200.00, saldo_livre=300.00,
        previsao_valor_custeio=150.00, previsao_valor_capital=250.00, previsao_valor_livre=350.00)
    receita_prevista_pdde_factory.create(
        paa=paa, acao_pdde=acao_pdde2,
        saldo_custeio=50.00, saldo_capital=100.00, saldo_livre=150.00,
        previsao_valor_custeio=75.00, previsao_valor_capital=125.00, previsao_valor_livre=175.00)

    # Testa com page_size inválido (deve usar padrão 1000)
    response = jwt_authenticated_client_sme.get(f"/api/programas-pdde/totais/?paa_uuid={paa.uuid}&page_size=abc")

    assert response.status_code == status.HTTP_200_OK
    assert 'programas' in response.data
    assert 'total' in response.data
    # Verifica se retornou todos os programas (3 programas criados) pois page_size inválido usa padrão
    assert len(response.data["programas"]) == 3

