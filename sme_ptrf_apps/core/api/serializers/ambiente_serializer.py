from rest_framework import serializers
from ...models import Ambiente


class AmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ambiente
        fields = ('id', 'prefixo', 'nome')
