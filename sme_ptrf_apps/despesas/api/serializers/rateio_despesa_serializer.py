from rest_framework import serializers

from .especificacao_material_servico_serializer import (
    EspecificacaoMaterialServicoLookUpSerializer,
    EspecificacaoMaterialServicoSerializer,
)
from .tipo_custeio_serializer import TipoCusteioSerializer
from ...models import Despesa, RateioDespesa
from ....core.api.serializers import TagLookupSerializer
from ....core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer, AcaoAssociacaoSerializer
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoSerializer, ContaAssociacaoLookUpSerializer
from ....core.models import AcaoAssociacao, Associacao, ContaAssociacao, Tag


class RateioDespesaSerializer(serializers.ModelSerializer):
    despesa = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=Despesa.objects.all()
    )
    associacao = AssociacaoSerializer()
    conta_associacao = ContaAssociacaoSerializer()
    acao_associacao = AcaoAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    tipo_custeio = TipoCusteioSerializer()
    tag = TagLookupSerializer()
    estorno = serializers.SerializerMethodField(method_name="get_estorno")

    def get_estorno(self, rateio):
        from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaLookUpSerializer
        estorno = rateio.estorno.first()
        return ReceitaLookUpSerializer(estorno, many=False).data

    class Meta:
        model = RateioDespesa
        fields = '__all__'


class RateioDespesaCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    conta_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ContaAssociacao.objects.all(),
        allow_null=True
    )

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AcaoAssociacao.objects.all(),
        allow_null=True
    )

    tag = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Tag.objects.all(),
        allow_null=True
    )

    class Meta:
        model = RateioDespesa
        exclude = ('id', 'despesa')


class RateioDespesaListaSerializer(serializers.ModelSerializer):
    despesa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Despesa.objects.all()
    )
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    conta_associacao = ContaAssociacaoLookUpSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoLookUpSerializer()
    numero_documento = serializers.SerializerMethodField('get_numero_documento')
    status_despesa = serializers.SerializerMethodField('get_status_despesa')
    data_documento = serializers.SerializerMethodField('get_data_documento')
    valor_total = serializers.SerializerMethodField('get_valor_total')
    tipo_documento_nome = serializers.SerializerMethodField('get_tipo_documento_nome')
    tipo_transacao_nome = serializers.SerializerMethodField('get_tipo_transacao_nome')
    cpf_cnpj_fornecedor = serializers.SerializerMethodField('get_cpf_cnpj_fornecedor')
    nome_fornecedor = serializers.SerializerMethodField('get_nome_fornecedor')
    data_transacao = serializers.SerializerMethodField('get_data_transacao')
    receitas_saida_do_recurso = serializers.SerializerMethodField('get_recurso_externo')
    estorno = serializers.SerializerMethodField(method_name="get_estorno")

    def get_numero_documento(self, rateio):
        return rateio.despesa.numero_documento

    def get_status_despesa(self, rateio):
        return rateio.despesa.status

    def get_data_documento(self, rateio):
        return rateio.despesa.data_documento

    def get_valor_total(self, rateio):
        return rateio.valor_rateio

    def get_tipo_documento_nome(self, rateio):
        return rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''

    def get_tipo_transacao_nome(self, rateio):
        return rateio.despesa.tipo_transacao.nome if rateio.despesa.tipo_transacao else ''

    def get_cpf_cnpj_fornecedor(self, rateio):
        return rateio.despesa.cpf_cnpj_fornecedor

    def get_nome_fornecedor(self, rateio):
        return rateio.despesa.nome_fornecedor

    def get_data_transacao(self, rateio):
        return rateio.despesa.data_transacao

    def get_recurso_externo(self, rateio):
        return rateio.despesa.receitas_saida_do_recurso.first().uuid if rateio.despesa.receitas_saida_do_recurso.exists() else None

    def get_estorno(self, rateio):
        return rateio.estorno.first()

    class Meta:
        model = RateioDespesa
        fields = (
            'uuid',
            'despesa',
            'numero_documento',
            'status_despesa',
            'especificacao_material_servico',
            'data_documento', 'aplicacao_recurso',
            'acao_associacao',
            'valor_total',
            'conferido',
            'cpf_cnpj_fornecedor',
            'nome_fornecedor',
            'tipo_documento_nome',
            'tipo_transacao_nome',
            'data_transacao',
            'notificar_dias_nao_conferido',
            'receitas_saida_do_recurso',
            'conta_associacao',
            'estorno',
        )


class RateioDespesaConciliacaoSerializer(serializers.ModelSerializer):
    acao_associacao = AcaoAssociacaoLookUpSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoLookUpSerializer()
    tipo_custeio = TipoCusteioSerializer()
    tag = TagLookupSerializer()

    class Meta:
        model = RateioDespesa
        fields = (
            'uuid',
            'especificacao_material_servico',
            'aplicacao_recurso',
            'acao_associacao',
            'valor_rateio',
            'conferido',
            'notificar_dias_nao_conferido',
            'tipo_custeio',
            'tag',
        )


class RateioDespesaTabelaGastosEscolaSerializer(serializers.ModelSerializer):
    despesa = serializers.SlugRelatedField(
        slug_field='id',
        required=False,
        queryset=Despesa.objects.all()
    )
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )
    conta_associacao = ContaAssociacaoSerializer()
    acao_associacao = AcaoAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    tipo_custeio = TipoCusteioSerializer()
    tag = TagLookupSerializer()
    estorno = serializers.SerializerMethodField(method_name="get_estorno")

    def get_estorno(self, rateio):
        from sme_ptrf_apps.receitas.api.serializers.receita_serializer import ReceitaLookUpSerializer
        estorno = rateio.estorno.first()
        return ReceitaLookUpSerializer(estorno, many=False).data

    class Meta:
        model = RateioDespesa
        fields = '__all__'


class RateioDespesaEstornoLookupSerializer(serializers.ModelSerializer):
    despesa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Despesa.objects.all()
    )
    associacao = AssociacaoSerializer()
    conta_associacao = ContaAssociacaoSerializer()
    acao_associacao = AcaoAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    tipo_custeio = TipoCusteioSerializer()
    tag = TagLookupSerializer()

    def get_estorno(self, rateio):
        return rateio.estorno.first()

    class Meta:
        model = RateioDespesa
        fields = '__all__'
