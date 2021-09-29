from rest_framework import serializers

from ...models import TipoAcertoDocumento


class TipoAcertoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAcertoDocumento
        fields = ('id', 'nome', 'uuid')
