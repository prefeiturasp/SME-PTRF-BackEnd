from rest_framework import serializers
from sme_ptrf_apps.core.models import Unidade

class ExportacaoDadosSerializer(serializers.Serializer):
    data_inicio = serializers.DateField(required=False, error_messages={
        'invalid': 'Formato de data inválido para data_inicio. Use YYYY-MM-DD.',
    })
    data_final = serializers.DateField(required=False, error_messages={
        'invalid': 'Formato de data inválido para data_final. Use YYYY-MM-DD.',
    })
    dre_uuid = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        allow_null=True,
        queryset=Unidade.dres.all(), error_messages={
            'does_not_exist': 'Unidade DRE não encontrada.'
        }
    )

