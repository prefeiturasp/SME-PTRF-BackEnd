from rest_framework import serializers

from sme_ptrf_apps.paa.models import ModeloCargaPaa


class ModeloCargaPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados de um modelo de carga do PAA.
    """
    class Meta:
        model = ModeloCargaPaa
        fields = '__all__'
