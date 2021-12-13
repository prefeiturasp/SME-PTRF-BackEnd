from rest_framework import serializers

from ...models import AnoAnaliseRegularidade


class AnoAnaliseRegularidadeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnoAnaliseRegularidade
        fields = ('ano', )
