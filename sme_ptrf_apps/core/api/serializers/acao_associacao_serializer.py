from rest_framework import serializers

from ..serializers.acao_serializer import AcaoSerializer
from ..serializers.associacao_serializer import AssociacaoSerializer
from ...models import AcaoAssociacao


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
        fields = ('uuid', 'id', 'nome')
