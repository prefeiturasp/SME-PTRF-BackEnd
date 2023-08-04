import logging

from rest_framework import serializers

logger = logging.getLogger(__name__)

class MandatoValidateSerializer(serializers.Serializer): # noqa
    referencia_mandato = serializers.CharField(required=True)
    data_inicial = serializers.DateField(required=True)
    data_final = serializers.DateField(required=True)

    def validate_data_inicial(self, value):
        pass
