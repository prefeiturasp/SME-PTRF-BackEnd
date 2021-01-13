from rest_framework import serializers

from ...models import Acao


class AcaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acao
        fields = ('id', 'uuid', 'nome', 'e_recursos_proprios')
