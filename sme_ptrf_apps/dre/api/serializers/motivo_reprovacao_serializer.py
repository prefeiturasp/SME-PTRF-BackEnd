from rest_framework import serializers

from ...models import MotivoReprovacao


class MotivoReprovacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoReprovacao
        fields = ('uuid', 'motivo')
