from rest_framework import serializers

from ...models import Comissao


class ComissaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comissao
        fields = ('uuid', 'id', 'nome')
