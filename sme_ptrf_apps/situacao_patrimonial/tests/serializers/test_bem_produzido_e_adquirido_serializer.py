import pytest
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_e_adquirido_serializer import BemProduzidoEAdquiridoSerializer

pytestmark = pytest.mark.django_db


def test_bem_produzido_e_adquirido_serializer(bem_produzido_item_1, rateio_1):
    serializer = BemProduzidoEAdquiridoSerializer(bem_produzido_item_1)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert 'numero_documento' in serializer.data
    assert serializer.data['especificacao_do_bem']
    assert serializer.data['data_aquisicao_producao']
    assert serializer.data['num_processo_incorporacao']
    assert serializer.data['periodo'] is None
    assert serializer.data['quantidade']
    assert serializer.data['valor_total']
    assert 'despesas' in serializer.data
    assert 'tipo' in serializer.data and serializer.data['tipo'] == 'Produzido'

    serializer = BemProduzidoEAdquiridoSerializer(rateio_1)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert serializer.data['numero_documento']
    assert serializer.data['especificacao_do_bem']
    assert serializer.data['data_aquisicao_producao']
    assert serializer.data['num_processo_incorporacao']
    assert serializer.data['periodo'] is None
    assert serializer.data['quantidade']
    assert serializer.data['valor_total']
    assert 'despesas' not in serializer.data
    assert 'tipo' in serializer.data and serializer.data['tipo'] == 'Adquirido'
