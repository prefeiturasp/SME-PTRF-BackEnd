from rest_framework import serializers

from ...models import TipoCusteio


class TipoCusteioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCusteio
        fields = ('id', 'nome')
