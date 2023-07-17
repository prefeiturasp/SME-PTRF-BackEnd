from rest_framework import serializers

from ...models import TipoConta


class TipoContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoConta
        fields = ('uuid', 'id', 'nome', 'banco_nome', 'agencia', 'numero_conta', 'numero_cartao', 'apenas_leitura', 'permite_inativacao')
