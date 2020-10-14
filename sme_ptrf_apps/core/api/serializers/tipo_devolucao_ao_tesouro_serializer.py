from rest_framework import serializers

from ...models import TipoDevolucaoAoTesouro


class TipoDevolucaoAoTesouroSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDevolucaoAoTesouro
        fields = ('id', 'nome')
