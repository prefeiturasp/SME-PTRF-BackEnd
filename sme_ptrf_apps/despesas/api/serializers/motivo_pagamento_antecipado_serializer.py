from rest_framework import serializers
from ...models import MotivoPagamentoAntecipado


class MotivoPagamentoAntecipadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoPagamentoAntecipado
        fields = ('id', 'motivo')
