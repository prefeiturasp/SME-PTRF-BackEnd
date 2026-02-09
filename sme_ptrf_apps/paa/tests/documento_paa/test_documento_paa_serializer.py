# import pytest

# from ...api.serializers import OutroRecursoSerializer

# pytestmark = pytest.mark.django_db


# def test_outros_recursos_list_serializer(outros_recursos):
#     serializer = OutroRecursoSerializer(outros_recursos)
#     assert serializer.data is not None
#     assert 'uuid' in serializer.data
#     assert 'nome' in serializer.data
#     assert 'aceita_capital' in serializer.data
#     assert 'aceita_custeio' in serializer.data
#     assert 'aceita_livre_aplicacao' in serializer.data
