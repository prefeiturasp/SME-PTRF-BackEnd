from rest_framework import serializers
from datetime import date

class ConsolidadoDreDevolverSerializer(serializers.Serializer): # noqa
    data_limite = serializers.DateField(required=True)

    def validate_data_limite(self, value):
        if value < date.today():
            raise serializers.ValidationError(f"Data limite precisa ser posterior a hoje ({date.today()}).")
        return value
