from rest_framework import serializers

from .especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from .tipo_custeio_serializer import TipoCusteioSerializer
from ...models import RateioDespesa, Despesa
from ....core.api.serializers.acao_associacao_serializer import AcaoAssociacaoSerializer
from ....core.api.serializers.associacao_serializer import AssociacaoSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoSerializer
from ....core.models import Associacao, ContaAssociacao, AcaoAssociacao


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
        queryset=ContaAssociacao.objects.all()
    )

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AcaoAssociacao.objects.all()
    )


    class Meta:
        model = RateioDespesa
        exclude = ('id', 'despesa')
