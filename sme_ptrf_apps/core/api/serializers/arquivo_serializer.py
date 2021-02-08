from rest_framework import serializers

from sme_ptrf_apps.core.models import Arquivo


class ArquivoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Arquivo
        fields = '__all__'
