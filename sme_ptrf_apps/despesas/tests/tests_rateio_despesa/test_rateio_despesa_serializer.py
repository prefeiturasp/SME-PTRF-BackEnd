import pytest

from ...api.serializers.rateio_despesa_serializer import (
    RateioDespesaSerializer,
    RateioDespesaListaSerializer,
    RateioDespesaTabelaGastosEscolaSerializer,
)

pytestmark = pytest.mark.django_db


def test_serializer(rateio_despesa_capital):
    serializer = RateioDespesaSerializer(rateio_despesa_capital)

    assert serializer.data is not None
    assert serializer.data['id']
    assert serializer.data['despesa']
    assert serializer.data['associacao']
    assert serializer.data['conta_associacao']
    assert serializer.data['acao_associacao']
    assert serializer.data['aplicacao_recurso']
    assert serializer.data['tipo_custeio']
    assert serializer.data['especificacao_material_servico']
    assert serializer.data['valor_rateio']
    assert serializer.data['quantidade_itens_capital']
    assert serializer.data['valor_item_capital']
    assert serializer.data['numero_processo_incorporacao_capital']


def test_serializer_lista(rateio_despesa_capital):
    serializer = RateioDespesaListaSerializer(rateio_despesa_capital)

    expected_fields = (
        'uuid',
        'despesa',
        'numero_documento',
        'status_despesa',
        'especificacao_material_servico',
        'data_documento',
        'aplicacao_recurso',
        'acao_associacao',
        'valor_total',
        'conferido',
        'cpf_cnpj_fornecedor',
        'nome_fornecedor',
        'tipo_documento_nome',
        'tipo_transacao_nome',
        'data_transacao',
        'notificar_dias_nao_conferido',
    )
    assert serializer.data is not None
    for field in expected_fields:
        assert serializer.data[field] is not None

    assert serializer.data['estorno'] is None


class TestRateioDespesaTabelaGastosEscolaSerializer:
    def test_retorna_dados(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert serializer.data is not None

    def test_campos_esperados_presentes(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        data = serializer.data

        expected_fields = (
            'id',
            'uuid',
            'despesa',
            'associacao',
            'conta_associacao',
            'acao_associacao',
            'aplicacao_recurso',
            'tipo_custeio',
            'especificacao_material_servico',
            'valor_rateio',
            'quantidade_itens_capital',
            'valor_item_capital',
            'numero_processo_incorporacao_capital',
            'conferido',
            'tag',
            'estorno',
            'periodo_conciliacao',
        )
        for field in expected_fields:
            assert field in data, f"Campo '{field}' ausente no serializer"

    def test_despesa_serializado_como_id(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert serializer.data['despesa'] == rateio_despesa_capital.despesa.id

    def test_associacao_serializado_como_uuid(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert str(serializer.data['associacao']) == str(rateio_despesa_capital.associacao.uuid)

    def test_periodo_conciliacao_serializado_como_referencia(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert serializer.data['periodo_conciliacao'] == rateio_despesa_capital.periodo_conciliacao.referencia

    def test_periodo_conciliacao_none_quando_ausente(self, rateio_despesa_capital):
        rateio_despesa_capital.periodo_conciliacao = None
        rateio_despesa_capital.save()

        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert serializer.data['periodo_conciliacao'] is None

    def test_estorno_none_quando_ausente(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        estorno = serializer.data['estorno']

        # get_estorno usa ReceitaLookUpSerializer(None).data — retorna dict com campos nulos
        assert isinstance(estorno, dict)
        assert estorno['data'] is None
        assert estorno['valor'] is None

    def test_conta_associacao_serializado_como_objeto(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        conta = serializer.data['conta_associacao']

        assert isinstance(conta, dict)
        assert 'uuid' in conta

    def test_acao_associacao_serializado_como_objeto(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        acao = serializer.data['acao_associacao']

        assert isinstance(acao, dict)
        assert 'uuid' in acao

    def test_especificacao_material_servico_serializado_como_objeto(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        especificacao = serializer.data['especificacao_material_servico']

        assert isinstance(especificacao, dict)
        assert 'id' in especificacao

    def test_tipo_custeio_serializado_como_objeto(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        tipo_custeio = serializer.data['tipo_custeio']

        assert isinstance(tipo_custeio, dict)
        assert 'id' in tipo_custeio

    def test_valor_rateio(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert float(serializer.data['valor_rateio']) == float(rateio_despesa_capital.valor_rateio)

    def test_campos_capital(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)
        data = serializer.data

        assert data['quantidade_itens_capital'] == rateio_despesa_capital.quantidade_itens_capital
        assert float(data['valor_item_capital']) == float(rateio_despesa_capital.valor_item_capital)
        assert data['numero_processo_incorporacao_capital'] == (
            rateio_despesa_capital.numero_processo_incorporacao_capital)

    def test_tag_none_quando_ausente(self, rateio_despesa_capital):
        serializer = RateioDespesaTabelaGastosEscolaSerializer(rateio_despesa_capital)

        assert serializer.data['tag'] is None
