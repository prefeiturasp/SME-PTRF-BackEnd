from rest_framework import serializers

from sme_ptrf_apps.receitas.models import TipoReceita


class TipoReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReceita
        fields = ('id', 'nome')
