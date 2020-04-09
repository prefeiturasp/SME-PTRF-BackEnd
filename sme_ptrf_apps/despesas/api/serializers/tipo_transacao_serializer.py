from rest_framework import serializers

from ...models import TipoTransacao


class TipoTransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoTransacao
        fields = ('id', 'nome')
