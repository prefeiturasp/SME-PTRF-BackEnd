from rest_framework import serializers

class ConsolidadoDreEditarMotivoRetificacao(serializers.Serializer): # noqa
    motivo = serializers.CharField(required=True)

    def validate_motivo(self, value):
        if not value:
            raise serializers.ValidationError(f"É necessário informar o motivo da retificação.")
        return value
