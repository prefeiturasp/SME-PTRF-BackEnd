from rest_framework import serializers

from ...models import FaqCategoria


class FaqCategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqCategoria
        fields = ('uuid', 'nome')
