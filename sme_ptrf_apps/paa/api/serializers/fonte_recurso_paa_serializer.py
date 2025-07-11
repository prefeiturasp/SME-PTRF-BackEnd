from rest_framework import serializers

from sme_ptrf_apps.paa.models import FonteRecursoPaa


class FonteRecursoPaaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(error_messages={'required': 'Nome da fonte de recurso paa é obrigatório.'})

    class Meta:
        model = FonteRecursoPaa
        fields = ('id', 'uuid', 'nome')
