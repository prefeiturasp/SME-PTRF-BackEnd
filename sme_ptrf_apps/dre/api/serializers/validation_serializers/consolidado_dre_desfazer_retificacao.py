from rest_framework import serializers

from sme_ptrf_apps.core.models import PrestacaoConta


class ConsolidadoDreDesfazerRetificacaoSerializer(serializers.Serializer): # noqa
    lista_pcs = serializers.ListField(child=serializers.UUIDField(), required=True)
    motivo = serializers.CharField(required=True)
    deve_apagar_retificacao = serializers.BooleanField(required=True)

    def validate_lista_pcs(self, value):
        if not value:
            raise serializers.ValidationError(f"É necessário informar ao menos uma PC para retificar.")

        for pc_uuid in value:
            if not PrestacaoConta.by_uuid(pc_uuid):
                raise serializers.ValidationError(f"Não foi encontrada uma PC para o uuid {pc_uuid}.")

        return value

    def validate_motivo(self, value):
        if not value:
            raise serializers.ValidationError(f"É necessário informar o motivo da retificação.")
        return value


