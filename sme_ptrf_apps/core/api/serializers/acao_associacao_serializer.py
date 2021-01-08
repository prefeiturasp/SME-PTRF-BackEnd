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
    e_recursos_proprios = serializers.SerializerMethodField('get_recurso_proprio')

    def get_nome_acao(self, obj):
        return obj.acao.nome

    def get_recurso_proprio(self, obj):
        return obj.acao.e_recursos_proprios

    class Meta:
        model = AcaoAssociacao
        fields = ('uuid', 'id', 'nome', 'e_recursos_proprios')
