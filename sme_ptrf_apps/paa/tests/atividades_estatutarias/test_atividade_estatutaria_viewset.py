import pytest
import uuid
from django.urls import reverse

from rest_framework import status
from sme_ptrf_apps.paa.choices import StatusChoices, Mes
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria
from sme_ptrf_apps.paa.api.serializers import AtividadeEstatutariaSerializer


@pytest.mark.django_db
def test_list_default_atividade_estatutaria(jwt_authenticated_client_sme, flag_paa):
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 0
    assert 'count' in result
    assert result['count'] == 0
    assert 'next' in result['links']
    assert result['links']['next'] is None
    assert 'previous' in result['links']
    assert result['links']['previous'] is None


@pytest.mark.django_db
def test_list_atividades_estatutarias(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 2
    assert result['count'] == 2


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_ativo(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"status": StatusChoices.ATIVO})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert result['count'] == 1


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_inativo(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"status": StatusChoices.INATIVO})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert result['count'] == 1


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_mes(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2

    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"mes": atividade_estatutaria_ativo.mes})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert result['count'] == 1


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_tipo(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2

    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"tipo": atividade_estatutaria_ativo.tipo})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert result['count'] == 1


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_nome_completo(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2

    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"nome": atividade_estatutaria_ativo.nome})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 1
    assert result['count'] == 1


@pytest.mark.django_db
def test_list_atividades_estatutarias_filtro_nome_parcial(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo, atividade_estatutaria_inativo):

    assert AtividadeEstatutaria.objects.count() == 2

    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.get(url, {"nome": atividade_estatutaria_ativo.nome[:-2]})
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in result
    assert len(result['results']) == 2
    assert result['count'] == 2


@pytest.mark.django_db
def test_list_tabelas_endpoint(jwt_authenticated_client_sme, flag_paa):
    url = reverse("api:atividades-estatutarias-tabelas")
    response = jwt_authenticated_client_sme.get(url)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert result['status'] == StatusChoices.to_dict()
    assert result['tipo'] == TipoAtividadeEstatutariaEnum.to_dict()
    assert result['mes'] == Mes.to_dict()


@pytest.mark.django_db
def test_cria_atividade_estatutaria_sem_nome(jwt_authenticated_client_sme, flag_paa):
    data = {}
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert AtividadeEstatutariaSerializer.MSG_NOME_NAO_INFORMADO in result['nome'], result['nome']
    assert AtividadeEstatutariaSerializer.MSG_MES_NAO_INFORMADO in result['mes'], result['mes']
    assert AtividadeEstatutariaSerializer.MSG_TIPO_NAO_INFORMADO in result['tipo'], result['tipo']
    assert AtividadeEstatutariaSerializer.MSG_STATUS_NAO_INFORMADO in result['status'], result['status']
    assert result.keys() == {'nome', 'tipo', 'mes', 'status'}, result.keys()


@pytest.mark.django_db
def test_cria_atividade_estatutaria_com_nome_vazio(jwt_authenticated_client_sme, flag_paa):
    data = {
        'nome': '',
        'tipo': 'ORDINARIA',
        'mes': 1,
        'status': 1
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert AtividadeEstatutariaSerializer.MSG_NOME_NAO_INFORMADO in result['nome'], result['nome']
    assert result.keys() == {'nome'}, result.keys()


@pytest.mark.django_db
def test_cria_atividade_estatutaria_com_mes_invalido(jwt_authenticated_client_sme, flag_paa):
    data = {
        'nome': 'Teste',
        'tipo': 'ORDINARIA',
        'mes': 13,
        'status': 1
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Valor inválido para o Mês.' in result['mes'], result['mes']


@pytest.mark.django_db
def test_cria_atividade_estatutaria_com_tipo_invalido(jwt_authenticated_client_sme, flag_paa):
    data = {
        'nome': 'Teste',
        'mes': 1,
        'tipo': 0,
        'status': 1
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Valor inválido para o Tipo da Atividade Estatutária.' in result['tipo']


@pytest.mark.django_db
def test_cria_atividade_estatutaria_com_sucesso(jwt_authenticated_client_sme, flag_paa):
    data = {
        "nome": "Teste",
        "status": 1,
        "mes": 1,
        "tipo": "ORDINARIA"
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert AtividadeEstatutaria.objects.count() == 1
    assert AtividadeEstatutaria.objects.filter(status=True, nome="Teste").count() == 1

    data = {
        "status": 0,
        "nome": "Teste 2",
        "mes": 1,
        "tipo": "ORDINARIA"
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert AtividadeEstatutaria.objects.count() == 2
    assert AtividadeEstatutaria.objects.filter(status=False, nome="Teste 2").count() == 1


@pytest.mark.django_db
def test_cria_atividade_estatutaria_duplicada(jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_ativo):
    data = {
        "nome": atividade_estatutaria_ativo.nome,
        "status": int(atividade_estatutaria_ativo.status),
        "mes": atividade_estatutaria_ativo.mes,
        "tipo": atividade_estatutaria_ativo.tipo
    }
    url = reverse("api:atividades-estatutarias-list")
    response = jwt_authenticated_client_sme.post(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['non_field_errors'] == ['Esta atividade estatutária já existe.'], result['non_field_errors']
    assert AtividadeEstatutaria.objects.count() == 1


@pytest.mark.django_db
def test_edita_atividade_estatutaria_duplicada_com_existencia(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_factory):

    obj = atividade_estatutaria_factory.create(nome="Atividade 1", paa=None)
    obj2 = atividade_estatutaria_factory.create(nome="Atividade 2", paa=None)
    data = {
        "nome": obj.nome,
        "tipo": obj.tipo,
        "mes": obj.mes,
    }
    url = reverse("api:atividades-estatutarias-detail", args=[obj2.uuid])
    response = jwt_authenticated_client_sme.patch(url, data)
    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result['non_field_errors'] == ['Esta atividade estatutária já existe.'], result['non_field_errors']
    assert AtividadeEstatutaria.objects.count() == 2


@pytest.mark.django_db
def test_edita_atividade_estatutaria_duplicada_com_propria_instancia(
        jwt_authenticated_client_sme, flag_paa, atividade_estatutaria_factory):

    obj = atividade_estatutaria_factory.create(nome="Atividade 1", paa=None)
    data = {
        "nome": obj.nome,
        "tipo": obj.tipo,
        "mes": obj.mes,
    }
    url = reverse("api:atividades-estatutarias-detail", args=[obj.uuid])
    response = jwt_authenticated_client_sme.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert AtividadeEstatutaria.objects.count() == 1


@pytest.mark.django_db
def test_patch_atividade_estatutaria(jwt_authenticated_client_sme, atividade_estatutaria_factory):
    obj = atividade_estatutaria_factory.create(nome="Antigo Nome", paa=None)
    url = reverse("api:atividades-estatutarias-detail", args=[obj.uuid])
    response = jwt_authenticated_client_sme.patch(url, {"nome": "Nome Atualizado"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    obj.refresh_from_db()
    assert obj.nome == "Nome Atualizado"


@pytest.mark.django_db
def test_delete_atividade_estatutaria(jwt_authenticated_client_sme, atividade_estatutaria_factory):
    obj = atividade_estatutaria_factory.create(nome="A Deletar", paa=None)
    url = reverse("api:atividades-estatutarias-detail", args=[obj.uuid])
    response = jwt_authenticated_client_sme.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not AtividadeEstatutaria.objects.filter(uuid=obj.uuid).exists()


@pytest.mark.django_db
def test_ordena_atividade_estatutaria_movendo_para_cima(
    jwt_authenticated_client_sme
):
    a1 = AtividadeEstatutaria.objects.create(nome="A", mes=1, tipo="ORDINARIA", ordem=1)
    a2 = AtividadeEstatutaria.objects.create(nome="B", mes=1, tipo="ORDINARIA", ordem=2)
    a3 = AtividadeEstatutaria.objects.create(nome="C", mes=1, tipo="ORDINARIA", ordem=3)
    a4 = AtividadeEstatutaria.objects.create(nome="D", mes=1, tipo="ORDINARIA", ordem=4)

    url = reverse(
        "api:atividades-estatutarias-ordenar",
        kwargs={"uuid": str(a4.uuid)},
    )

    payload = {"destino": str(a2.uuid)}

    response = jwt_authenticated_client_sme.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    a1.refresh_from_db()
    a2.refresh_from_db()
    a3.refresh_from_db()
    a4.refresh_from_db()

    assert a1.ordem == 1
    assert a4.ordem == 2
    assert a2.ordem == 3
    assert a3.ordem == 4


@pytest.mark.django_db
def test_ordena_atividade_estatutaria_movendo_para_baixo(
    jwt_authenticated_client_sme
):
    a1 = AtividadeEstatutaria.objects.create(nome="A", mes=1, tipo="ORDINARIA", ordem=1)
    a2 = AtividadeEstatutaria.objects.create(nome="B", mes=1, tipo="ORDINARIA", ordem=2)
    a3 = AtividadeEstatutaria.objects.create(nome="C", mes=1, tipo="ORDINARIA", ordem=3)
    a4 = AtividadeEstatutaria.objects.create(nome="D", mes=1, tipo="ORDINARIA", ordem=4)

    url = reverse(
        "api:atividades-estatutarias-ordenar",
        kwargs={"uuid": a2.uuid},
    )

    payload = {"destino": str(a4.uuid)}
    response = jwt_authenticated_client_sme.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK

    a1.refresh_from_db()
    a2.refresh_from_db()
    a3.refresh_from_db()
    a4.refresh_from_db()

    assert a1.ordem == 1
    assert a3.ordem == 2
    assert a4.ordem == 3
    assert a2.ordem == 4


@pytest.mark.django_db
def test_ordena_atividade_estatutaria_destino_inexistente(
    jwt_authenticated_client_sme
):
    atividade = AtividadeEstatutaria.objects.create(
        nome="A", mes=1, tipo="ORDINARIA", ordem=1
    )

    url = reverse(
        "api:atividades-estatutarias-ordenar",
        kwargs={"uuid": atividade.uuid},
    )

    payload = {"destino": str(uuid.uuid4())}

    response = jwt_authenticated_client_sme.patch(url, payload, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND
