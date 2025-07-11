from rest_framework import serializers

from sme_ptrf_apps.paa.models import AcaoPdde, ProgramaPdde
from sme_ptrf_apps.paa.api.serializers.programa_pdde_serializer import ProgramaPddeSerializer


class AcaoPddeSimplesSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcaoPdde
        fields = ('uuid', 'nome')


class AcaoPddeSerializer(serializers.ModelSerializer):
    programa = serializers.SlugRelatedField(queryset=ProgramaPdde.objects.all(), slug_field='uuid')
    programa_objeto = ProgramaPddeSerializer(read_only=True, many=False)

    class Meta:
        model = AcaoPdde
        fields = ('id', 'uuid', 'nome', 'programa', 'programa_objeto',
                  'aceita_capital', 'aceita_custeio', 'aceita_livre_aplicacao')
        read_only_fields = ('id', 'uuid', 'programa', 'programa_objeto')
