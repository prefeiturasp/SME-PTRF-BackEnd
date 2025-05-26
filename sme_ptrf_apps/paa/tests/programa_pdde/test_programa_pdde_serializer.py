import pytest

from sme_ptrf_apps.paa.api.serializers import ProgramaPddeSerializer  # ProgramasPddeSomatorioTotalSerializer


pytestmark = pytest.mark.django_db


def test_programa_pdde_list_serializer(programa_pdde):
    serializer = ProgramaPddeSerializer(programa_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data
    assert 'pode_ser_excluida' in serializer.data


# def test_programa_pdde_somatorio_serializer(programa_pdde, programa_pdde_2, programa_pdde_3, acao_pdde_factory):
#     acao_pdde_factory.create(
#         programa=programa_pdde,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     acao_pdde_factory.create(
#         programa=programa_pdde,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     acao_pdde_factory.create(
#         programa=programa_pdde_2,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     acao_pdde_factory.create(
#         programa=programa_pdde_2,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     acao_pdde_factory.create(
#         programa=programa_pdde_3,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     acao_pdde_factory.create(
#         programa=programa_pdde_3,
#         aceita_capital=True,
#         aceita_custeio=True,
#         aceita_livre_aplicacao=True,
#         saldo_valor_custeio=110.00,
#         saldo_valor_capital=150.00,
#         saldo_valor_livre_aplicacao=200.00,
#         previsao_valor_custeio=140.00,
#         previsao_valor_capital=312.00,
#         previsao_valor_livre_aplicacao=415.00
#     )
#     serializer = ProgramasPddeSomatorioTotalSerializer(instance=None)
#     data = serializer.to_representation(None)

#     assert 'programas' in data
#     assert 'total' in data
#     assert data["total"] == {
#         "total_valor_custeio": 1500.00,
#         "total_valor_capital": 2772.00,
#         "total_valor_livre_aplicacao": 3690.00,
#         "total": 7962.00
#     }
#     assert data["programas"][0]["nome"] == "Programa PDDE Teste"
#     assert data["programas"][0]["total_valor_custeio"] == 500.00
#     assert data["programas"][1]["nome"] == "Programa PDDE Teste 2"
#     assert data["programas"][1]["total_valor_custeio"] == 500.00
