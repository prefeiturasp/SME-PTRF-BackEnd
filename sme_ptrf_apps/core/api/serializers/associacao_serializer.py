from rest_framework import serializers

from ...models import Associacao, Unidade

from ...api.serializers.unidade_serializer import UnidadeSerializer, UnidadeLookUpSerializer

class AssociacaoSerializer(serializers.ModelSerializer):
    unidade = UnidadeLookUpSerializer(many=False)
    class Meta:
        model = Associacao
        fields ='__all__'


class AssociacaoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Associacao
        fields = ('id', 'nome')


class AssociacaoCreateSerializer(serializers.ModelSerializer):
    unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )
    class Meta:
        model = Associacao
        fields ='__all__'
