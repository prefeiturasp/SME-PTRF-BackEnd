from rest_framework import serializers

from sme_ptrf_apps.core.models import ModeloCarga


class ModeloCargaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModeloCarga
        fields = '__all__'
