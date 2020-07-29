from rest_framework import serializers

from ...api.serializers.unidade_serializer import (UnidadeInfoAtaSerializer, UnidadeLookUpSerializer,
                                                   UnidadeListSerializer)
from ...models import Associacao, Unidade


class AssociacaoSerializer(serializers.ModelSerializer):
    unidade = UnidadeLookUpSerializer(many=False)

    class Meta:
        model = Associacao
        fields = '__all__'


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
        fields = '__all__'


class AssociacaoInfoAtaSerializer(serializers.ModelSerializer):
    unidade = UnidadeInfoAtaSerializer(many=False)

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'cnpj',
            'unidade',
        ]


class AssociacaoListSerializer(serializers.ModelSerializer):
    unidade = UnidadeListSerializer(many=False)

    class Meta:
        model = Associacao
        fields = [
            'uuid',
            'nome',
            'unidade',
            'status_regularidade',
        ]
