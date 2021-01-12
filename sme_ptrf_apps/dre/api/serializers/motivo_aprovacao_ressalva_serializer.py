from rest_framework import serializers

from ...models import MotivoAprovacaoRessalva


class MotivoAprovacaoRessalvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoAprovacaoRessalva
        fields = ('uuid', 'motivo')
