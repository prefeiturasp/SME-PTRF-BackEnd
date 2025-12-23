from rest_framework import serializers, validators
from .outros_recursos_serializer import OutroRecursoSerializer

from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaOutroRecursoPeriodo, Paa, OutroRecursoPeriodoPaa)


class ReceitaPrevistaOutroRecursoPeriodoSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(
        queryset=Paa.objects.all(),
        slug_field='uuid',
        required=True,
        error_messages={
            'required': 'PAA não foi informado.',
            'null': 'PAA não foi informado.'
        },
    )
    outro_recurso_objeto = OutroRecursoSerializer(read_only=True, many=False)

    outro_recurso_periodo = serializers.SlugRelatedField(
        queryset=OutroRecursoPeriodoPaa.objects.filter(ativo=True),
        slug_field='uuid',
        required=True,
        error_messages={
            'required': 'Outro Recurso do Período não foi informado.',
            'null': 'Outro Recurso do Período não foi informado.'
        },
    )

    class Meta:
        model = ReceitaPrevistaOutroRecursoPeriodo
        fields = (
            'uuid', 'paa', 'outro_recurso_periodo',
            'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre',
            'saldo_custeio', 'saldo_capital', 'saldo_livre', 'outro_recurso_objeto'
        )
        read_only_fields = (
            'uuid', 'saldo_custeio', 'saldo_capital', 'saldo_livre',
            'criado_em', 'alterado_em', 'outro_recurso_objeto'
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ReceitaPrevistaOutroRecursoPeriodo.objects.all(),
                fields=['paa', 'outro_recurso_periodo'],
                message="Já existe uma receita cadastrada para o recurso no período!"
            ),
        ]
        ordering = ('outro_recurso_periodo__outro_recurso__nome',)
