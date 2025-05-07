from rest_framework import serializers

from sme_ptrf_apps.paa.models import Paa, PeriodoPaa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.services import PaaService

from . import PeriodoPaaSerializer


class PaaSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    periodo_paa_objeto = PeriodoPaaSerializer(read_only=True, many=False)

    class Meta:
        model = Paa
        fields = ('uuid', 'periodo_paa', 'associacao', 'periodo_paa_objeto')
        read_only_fields = ('periodo_paa_objeto', 'periodo_paa')

    def validate(self, attrs):
        try:
            PaaService.pode_elaborar_novo_paa()
        except Exception as exc:
            raise serializers.ValidationError({'non_field_errors': exc})

        try:
            periodo_paa = PeriodoPaa.periodo_vigente()
            attrs["periodo_paa"] = periodo_paa
        except PeriodoPaa.DoesNotExist:
            raise serializers.ValidationError({
                'non_field_errors': 'Nenhum Período vigente foi encontrado.'
            })

        return super().validate(attrs)

    def create(self, validated_data):
        periodo_paa = validated_data.get('periodo_paa')  # obtido pelo Service, o Período vigente em validate()
        associacao = validated_data.get('associacao')  # obtido pelo payload

        existe_paa = Paa.objects.filter(periodo_paa=periodo_paa, associacao=associacao).exists()
        if existe_paa:
            raise serializers.ValidationError({
                'non_field_errors': 'Já existe uma PAA para a Associação informada.'
                })

        instance = super().create(validated_data)
        return instance
