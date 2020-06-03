from rest_framework import serializers

from ...models import Ata


class AtaLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_conta')

    def get_nome_conta(self, obj):
        return obj.nome

    class Meta:
        model = Ata
        fields = ('uuid', 'nome', 'alterado_em')
