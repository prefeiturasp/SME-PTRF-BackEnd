from rest_framework import serializers

from sme_ptrf_apps.receitas.models import DetalheTipoReceita


class DetalheTipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalheTipoReceita
        fields = ('id', 'nome')
