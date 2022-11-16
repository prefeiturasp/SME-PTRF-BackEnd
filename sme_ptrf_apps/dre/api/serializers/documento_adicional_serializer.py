from rest_framework import serializers

from ...models import DocumentoAdicional


class DocumentoAdicionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentoAdicional
        fields = ('nome', 'arquivo', 'analises_de_documentos_do_documento_adicional')
