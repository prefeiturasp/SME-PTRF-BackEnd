from rest_framework import serializers

from sme_ptrf_apps.core.models import Recurso, Unidade
from sme_ptrf_apps.core.choices import AlertaPaginaCategoriaChoices


class AlertaPaginaQueryParamsSerializer(serializers.Serializer):
    recurso = serializers.UUIDField()
    unidade = serializers.UUIDField()
    categoria = serializers.ChoiceField(
        choices=AlertaPaginaCategoriaChoices.choices,
        default=AlertaPaginaCategoriaChoices.AVISO_REMOCAO_PRESIDENTE
    )

    def validate_recurso(self, valor):
        try:
            return Recurso.objects.get(uuid=valor)
        except Recurso.DoesNotExist:
            raise serializers.ValidationError('O recurso informado é inválido.')

    def validate_unidade(self, valor):
        try:
            return Unidade.objects.get(uuid=valor)
        except Unidade.DoesNotExist:
            raise serializers.ValidationError('A unidade informada é inválida.')


class AlertaPaginaTemplateSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    categoria = serializers.CharField()
    texto = serializers.CharField()
    data_ocorrencia = serializers.DateField()
    chave = serializers.CharField()


class AlertaPaginaResponseSerializer(serializers.Serializer):
    alerta = AlertaPaginaTemplateSerializer(allow_null=True)
