from rest_framework import serializers

from ...models import Unidade


class DreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'sigla')


class UnidadeLookUpSerializer(serializers.ModelSerializer):
    dre = DreSerializer()
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'tipo_unidade', 'nome', 'sigla', 'dre')


class UnidadeSerializer(serializers.ModelSerializer):
    dre = UnidadeLookUpSerializer()

    class Meta:
        model = Unidade
        fields = '__all__'


class UnidadeInfoAtaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unidade
        fields = ('tipo_unidade', 'nome')


class UnidadeListSerializer(serializers.ModelSerializer):
    # nome_com_tipo = serializers.SerializerMethodField('get_nome_com_tipo')
    # def get_nome_com_tipo(self, obj):
    #     return f'{obj.tipo_unidade} {obj.nome}'
    class Meta:
        model = Unidade
        fields = ('uuid', 'codigo_eol', 'nome_com_tipo',)
