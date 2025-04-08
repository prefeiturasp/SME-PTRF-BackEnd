import pytest

from ...api.serializers import CategoriaPddeSerializer, CategoriasPddeSomatorioTotalSerializer

pytestmark = pytest.mark.django_db


def test_categoria_pdde_list_serializer(categoria_pdde):
    serializer = CategoriaPddeSerializer(categoria_pdde)
    assert serializer.data is not None
    assert 'uuid' in serializer.data
    assert 'nome' in serializer.data


def test_categoria_pdde_somatorio_serializer(categoria_pdde, categoria_pdde_2, categoria_pdde_3, acao_pdde_factory):
    acao_pdde_factory.create(categoria=categoria_pdde, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True,
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    acao_pdde_factory.create(categoria=categoria_pdde, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True,
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    acao_pdde_factory.create(categoria=categoria_pdde_2, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True, 
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    acao_pdde_factory.create(categoria=categoria_pdde_2, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True, 
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    acao_pdde_factory.create(categoria=categoria_pdde_3, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True,
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    acao_pdde_factory.create(categoria=categoria_pdde_3, aceita_capital=True, aceita_custeio=True, aceita_livre_aplicacao=True,
                             saldo_valor_custeio=110.00, saldo_valor_capital=150.00, saldo_valor_livre_aplicacao=200.00,
                             previsao_valor_custeio=140.00, previsao_valor_capital=312.00, previsao_valor_livre_aplicacao=415.00)
    serializer = CategoriasPddeSomatorioTotalSerializer(instance=None)
    data = serializer.to_representation(None)

    assert 'categorias' in data
    assert 'total' in data
    assert data["total"] == {
        "total_valor_custeio": 1500.00,
        "total_valor_capital": 2772.00,
        "total_valor_livre_aplicacao": 3690.00,
        "total": 7962.00
    }
    assert data["categorias"][0]["nome"] == "Categoria PDDE Teste"
    assert data["categorias"][0]["total_valor_custeio"] == 500.00
    assert data["categorias"][1]["nome"] == "Categoria PDDE Teste 2"
    assert data["categorias"][1]["total_valor_custeio"] == 500.00
