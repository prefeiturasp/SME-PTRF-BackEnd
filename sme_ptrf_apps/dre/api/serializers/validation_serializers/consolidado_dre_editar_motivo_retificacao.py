from rest_framework import serializers

class ConsolidadoDreEditarMotivoRetificacao(serializers.Serializer): # noqa
    motivo = serializers.CharField(required=False, allow_null=True, allow_blank=True)

