# import json
# import pytest
# from unittest import mock

# from django.db.models.deletion import ProtectedError
# from rest_framework import status
# from sme_ptrf_apps.despesas.models import TipoTransacao
# from sme_ptrf_apps.despesas.api.views.tipos_transacao_viewset import TiposTransacaoViewSet

# pytestmark = pytest.mark.django_db



# @pytest.fixture
# def related_model():
#     return TipoTransacao.objects.create()


# @pytest.fixture
# def my_model(related_model):
#     return TipoTransacao.objects.create(related_field=related_model)


# def test_create(jwt_authenticated_client_d):

#     payload = {
#         'nome': 'Pix/Doc/Ted',
#     }

#     response = jwt_authenticated_client_d.post(
#         f'/api/tipos-transacao/', data=json.dumps(payload),
#         content_type='application/json'
#     )

#     result = json.loads(response.content)

#     assert response.status_code == status.HTTP_201_CREATED
#     assert TipoTransacao.objects.filter(uuid=result['uuid']).exists()


# def test_create_invalid_payload(jwt_authenticated_client_d):

#     payload = {
#         'nome2': 'Cheque',
#     }

#     response = jwt_authenticated_client_d.post(
#         f'/api/tipos-transacao/', data=json.dumps(payload),
#         content_type='application/json'
#     )

#     result = json.loads(response.content)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert TipoTransacao.objects.count() == 0


# def test_delete(jwt_authenticated_client_d, tipo_transacao_01):
#     assert TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()

#     response = jwt_authenticated_client_d.delete(
#         f'/api/tipos-transacao/{tipo_transacao_01.uuid}/',
#         content_type='application/json'
#     )

#     assert response.status_code == status.HTTP_204_NO_CONTENT
#     assert not TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()


# def test_delete_uuid_invalid(jwt_authenticated_client_d, tipo_transacao_01):
#     assert TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()

#     response = jwt_authenticated_client_d.delete(
#         f'/api/tipos-transacao/01829e9d-304b-47df-9725-234fe886600b/',
#         content_type='application/json'
#     )

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()


# @mock.patch.object(TiposTransacaoViewSet, "perform_destroy")
# def test_delete_exception(mock_perform_destroy, jwt_authenticated_client_d, tipo_transacao_01):
#     mock_perform_destroy.side_effect = ProtectedError("Erro", TipoTransacao)
#     assert TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()
    
#     response = jwt_authenticated_client_d.delete(
#         f'/api/tipos-transacao/{tipo_transacao_01.uuid}/',
#         content_type='application/json'
#     )

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert TipoTransacao.objects.filter(uuid=tipo_transacao_01.uuid).exists()


# def test_get(jwt_authenticated_client_d, tipo_transacao_01):
#     response = jwt_authenticated_client_d.get(
#         f'/api/tipos-transacao/{tipo_transacao_01.uuid}/',
#         content_type='applicaton/json'
#     )

#     result = json.loads(response.content)

#     resultado_esperado = {
#         'nome': tipo_transacao_01.nome,
#         'id': tipo_transacao_01.id,
#         'tem_documento': False,
#         'uuid': str(tipo_transacao_01.uuid)
#     }

#     assert response.status_code == status.HTTP_200_OK
#     assert result == resultado_esperado


# def test_get_invalid_uuid(jwt_authenticated_client_d, tipo_transacao_01):
#     response = jwt_authenticated_client_d.get(
#         f'/api/tipos-transacao/01829e9d-304b-47df-9725-234fe886600b/',
#         content_type='applicaton/json'
#     )

#     assert response.status_code == status.HTTP_404_NOT_FOUND


# def test_list_filtra_nome(jwt_authenticated_client_d, tipo_transacao_01, tipo_transacao_02):
#     response = jwt_authenticated_client_d.get(f'/api/tipos-transacao/?nome=Cheq', content_type='application/json')
#     result = json.loads(response.content)

#     resultado_esperado = [
#         {
#             'nome': tipo_transacao_01.nome,
#             'id': tipo_transacao_01.id,
#             'tem_documento': False,
#             'uuid': str(tipo_transacao_01.uuid)
#         },
#     ]

#     assert response.status_code == status.HTTP_200_OK
#     assert result == resultado_esperado
