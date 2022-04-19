from rest_framework import serializers

from ...models import TipoDocumento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome', 'apenas_digitos', 'numero_documento_digitado', 'pode_reter_imposto', 'eh_documento_de_retencao_de_imposto', 'documento_comprobatorio_de_despesa')


class TipoDocumentoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome')
