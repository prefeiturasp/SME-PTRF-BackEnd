from rest_framework import serializers

from ...models import TipoDocumentoPrestacaoConta


class TipoDocumentoPrestacaoContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumentoPrestacaoConta
        fields = ('id', 'uuid', 'nome', 'documento_por_conta')
