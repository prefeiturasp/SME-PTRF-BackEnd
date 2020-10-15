from rest_framework import serializers

from ...models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome', 'apenas_digitos', 'numero_documento_digitado')


class TipoDocumentoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome')
