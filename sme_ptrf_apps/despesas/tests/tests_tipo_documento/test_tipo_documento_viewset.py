import pytest
from rest_framework import status
from ....despesas.models import TipoDocumento, Despesa


@pytest.fixture
def tipo_documento():
    return TipoDocumento.objects.create(nome="Cupom")


@pytest.mark.django_db
def test_list_tipos_documento(jwt_authenticated_client, tipo_documento):
    url = "/api/tipos-documento/"
    response = jwt_authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == "Cupom"


@pytest.mark.django_db
def test_filter_tipos_documento_por_nome(jwt_authenticated_client, tipo_documento):
    url = "/api/tipos-documento/"
    response = jwt_authenticated_client.get(url, {'nome': 'Cup'})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['nome'] == "Cupom"


@pytest.mark.django_db
def test_criar_tipo_documento(jwt_authenticated_client):
    url = "/api/tipos-documento/"
    data = {"nome": "Recibo"}
    response = jwt_authenticated_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert TipoDocumento.objects.filter(nome="Recibo").exists()


@pytest.mark.django_db
def test_alterar_tipo_documento(jwt_authenticated_client, tipo_documento):
    url = f"/api/tipos-documento/{tipo_documento.uuid}/"
    data = {"nome": "Fatura"}
    response = jwt_authenticated_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    tipo_documento.refresh_from_db()
    assert tipo_documento.nome == "Fatura"


@pytest.mark.django_db
def test_excluir_tipo_documento_sem_despesa(jwt_authenticated_client, tipo_documento):
    url = f"/api/tipos-documento/{tipo_documento.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not TipoDocumento.objects.filter(uuid=tipo_documento.uuid).exists()


@pytest.mark.django_db
def test_excluir_tipo_documento_com_despesa(jwt_authenticated_client, tipo_documento):
    Despesa.objects.create(tipo_documento=tipo_documento)
    url = f"/api/tipos-documento/{tipo_documento.uuid}/"
    response = jwt_authenticated_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['erro'] == 'ProtectedError'
    assert response.data['mensagem'] == (
        'Essa operação não pode ser realizada. Há despesas cadastradas com esse tipo de documento.'
    )
    assert TipoDocumento.objects.filter(uuid=tipo_documento.uuid).exists()
