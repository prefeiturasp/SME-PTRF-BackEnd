from rest_framework import serializers

from ...models import AcaoAssociacao

from ..serializers.acao_serializer import AcaoSerializer
from ..serializers.associacao_serializer import AssociacaoSerializer


class AcaoAssociacaoSerializer(serializers.ModelSerializer):
    acao = AcaoSerializer()
    associacao = AssociacaoSerializer()

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'acao', 'associacao', 'status')


class AcaoAssociacaoLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_acao')

    def get_nome_acao(self, obj):
        return obj.acao.nome

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'nome')
