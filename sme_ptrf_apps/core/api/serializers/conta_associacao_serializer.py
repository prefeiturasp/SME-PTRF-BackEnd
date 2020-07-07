from rest_framework import serializers

from ..serializers.associacao_serializer import AssociacaoSerializer
from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ...models import ContaAssociacao, Associacao


class ContaAssociacaoSerializer(serializers.ModelSerializer):
    tipo_conta = TipoContaSerializer()
    associacao = AssociacaoSerializer()

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'tipo_conta', 'associacao', 'status')


class ContaAssociacaoLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_conta')

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'nome')


class ContaAssociacaoInfoAtaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_conta')

    def get_nome_conta(self, obj):
        return obj.tipo_conta.nome

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'nome', 'banco_nome', 'agencia', 'numero_conta', )


class ContaAssociacaoDadosSerializer(serializers.ModelSerializer):
    tipo_conta = TipoContaSerializer()

    class Meta:
        model = ContaAssociacao
        fields = ('uuid', 'tipo_conta', 'banco_nome', 'agencia', 'numero_conta', )


class ContaAssociacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaAssociacao
        exclude = ('id',)
