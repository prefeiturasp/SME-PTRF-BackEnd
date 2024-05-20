from rest_framework import serializers

from sme_ptrf_apps.core.models import Arquivo
from sme_ptrf_apps.core.models.periodo import Periodo


class ArquivoSerializer(serializers.ModelSerializer):
    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )
    class Meta:
        model = Arquivo
        fields = '__all__'