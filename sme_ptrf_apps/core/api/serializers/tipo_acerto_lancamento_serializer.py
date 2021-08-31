from rest_framework import serializers

from ...models import TipoAcertoLancamento


class TipoAcertoLancamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAcertoLancamento
        fields = ('id', 'nome', 'categoria', 'uuid')
