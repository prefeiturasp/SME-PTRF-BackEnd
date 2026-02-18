from rest_framework import serializers

from sme_ptrf_apps.paa.models import ModeloCargaPaa


class ModeloCargaPaaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ModeloCargaPaa
        fields = '__all__'
