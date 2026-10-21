from rest_framework import serializers
from sme_ptrf_apps.core.models import Periodo, PeriodoInicialAssociacao, Recurso
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoSerializer


class SimplePeriodoInicialAssociacaoSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(allow_blank=True, required=False)

    periodo_inicial = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all(),
    )

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Recurso.objects.all(),
    )

    status_valores_reprogramados = serializers.ChoiceField(
        choices=PeriodoInicialAssociacao.STATUS_VALORES_REPROGRAMADOS_CHOICES,
        required=False,
    )

    periodos_disponiveis = serializers.SerializerMethodField('get_periodos_disponiveis')

    def get_periodos_disponiveis(self, obj):
        periodos_disponiveis = Periodo.objects.filter(recurso=obj.recurso)

        return PeriodoSerializer(periodos_disponiveis, many=True).data

    class Meta:
        model = PeriodoInicialAssociacao
        fields = (
            'uuid',
            'periodo_inicial',
            'recurso',
            'status_valores_reprogramados',
            'periodos_disponiveis',
        )

    def validate(self, attrs):
        periodo_inicial = attrs.get('periodo_inicial')
        recurso = attrs.get('recurso')

        if periodo_inicial and recurso and periodo_inicial.recurso_id != recurso.id:
            raise serializers.ValidationError({
                'periodo_inicial': 'Período deve pertencer ao recurso selecionado.'
            })

        return attrs
