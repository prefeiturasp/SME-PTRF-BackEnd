from rest_framework import serializers

class ConsolidadoDreEditarMotivoRetificacao(serializers.Serializer): # noqa
    motivo = serializers.CharField(required=True, allow_null=True, allow_blank=True)
