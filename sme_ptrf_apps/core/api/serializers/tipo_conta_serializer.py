from rest_framework import serializers

from ...models import TipoConta


class TipoContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoConta
        fields = ('id', 'nome')
