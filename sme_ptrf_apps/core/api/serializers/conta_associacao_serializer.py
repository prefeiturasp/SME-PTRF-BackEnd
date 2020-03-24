from rest_framework import serializers

from ...models import ContaAssociacao

from ..serializers.tipo_conta_serializer import TipoContaSerializer
from ..serializers.associacao_serializer import AssociacaoSerializer


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
