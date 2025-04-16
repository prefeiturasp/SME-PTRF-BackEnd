from rest_framework import serializers

from sme_ptrf_apps.paa.models import PeriodoPaa


class PeriodoPaaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoPaa
        fields = ('id', 'referencia', 'data_inicial', 'data_final')
