import pytest
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_e_adquirido_serializer import BemProduzidoEAdquiridoSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa
from sme_ptrf_apps.core.models.periodo import Periodo

pytestmark = pytest.mark.django_db


def test_bem_produzido_e_adquirido_serializer(bem_produzido_item_1, rateio_1):
    serializer = BemProduzidoEAdquiridoSerializer(bem_produzido_item_1)

    assert serializer.data is not None
    assert serializer.data['uuid']
    assert 'numero_documento' in serializer.data
    assert serializer.data['especificacao_do_bem']
    # Para BemProduzidoItem, a data pode ser None caso não haja despesas com data_documento
    assert 'data_aquisicao_producao' in serializer.data
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


def test_bem_produzido_item_usa_data_documento_mais_recente_para_data_aquisicao_e_calcula_periodo_correspondente(
    bem_produzido_item_1,
    despesa_factory
):
    bem_produzido = bem_produzido_item_1.bem_produzido

    d1 = despesa_factory(associacao=bem_produzido.associacao, data_documento='2024-01-01', nome_fornecedor='F1', status='ATIVO')
    d2 = despesa_factory(associacao=bem_produzido.associacao, data_documento='2024-02-01', nome_fornecedor='F2', status='ATIVO')

    BemProduzidoDespesa.objects.create(bem_produzido=bem_produzido, despesa=d1)
    BemProduzidoDespesa.objects.create(bem_produzido=bem_produzido, despesa=d2)

    serializer = BemProduzidoEAdquiridoSerializer(bem_produzido_item_1)
    data = serializer.data

    assert str(data['data_aquisicao_producao']) == str(d2.data_documento)
    periodo_esperado = Periodo.da_data(data['data_aquisicao_producao'])
    assert data['periodo'] == (periodo_esperado.referencia if periodo_esperado else None)
