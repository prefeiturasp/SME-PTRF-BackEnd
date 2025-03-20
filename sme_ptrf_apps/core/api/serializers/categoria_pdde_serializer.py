from rest_framework import serializers

from ...models import CategoriaPdde


class CategoriaPddeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoriaPdde
        fields = ('id', 'uuid', 'nome')
