from rest_framework import serializers
from ...models import Lauda
from sme_ptrf_apps.core.api.serializers import TipoContaSerializer


class LaudaSerializer(serializers.ModelSerializer):
    consolidado_dre = serializers.SerializerMethodField()
    tipo_conta = TipoContaSerializer()
    usuario = serializers.SerializerMethodField(method_name="get_usuario", required=False, allow_null=True)

    def get_consolidado_dre(self, lauda):
        from .consolidado_dre_serializer import ConsolidadoDreSerializer
        if not lauda.consolidado_dre:
            return None
        return ConsolidadoDreSerializer(lauda.consolidado_dre).data

    def get_usuario(self, lauda):
        return lauda.usuario.username if lauda.usuario.username else ''

    class Meta:
        model = Lauda
        fields = (
            'uuid',
            'arquivo_lauda_txt',
            'arquivo_lauda_pdf',
            'consolidado_dre',
            'tipo_conta',
            'usuario',
            'status',
        )


class LaudaLookupSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField(method_name="get_usuario", required=False, allow_null=True)
    tipo_conta = TipoContaSerializer()

    def get_usuario(self, lauda):
        return lauda.usuario.username if lauda.usuario.username else ''

    class Meta:
        model = Lauda
        fields = (
            'uuid',
            'arquivo_lauda_txt',
            'arquivo_lauda_pdf',
            'usuario',
            'status',
            'tipo_conta',
            'alterado_em',
        )
