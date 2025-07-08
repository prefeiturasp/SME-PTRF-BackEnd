from rest_framework import serializers

from ...models import TipoCusteio


class TipoCusteioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCusteio
        fields = ('uuid', 'nome')


class TipoCusteioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCusteio
        fields = ('nome', 'id', 'uuid', 'eh_tributos_e_tarifas')
