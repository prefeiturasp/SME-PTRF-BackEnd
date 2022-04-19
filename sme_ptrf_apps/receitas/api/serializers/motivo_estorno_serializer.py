from rest_framework import serializers
from ...models import MotivoEstorno


class MotivoEstornoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoEstorno
        fields = ('id', 'uuid', 'motivo', )
