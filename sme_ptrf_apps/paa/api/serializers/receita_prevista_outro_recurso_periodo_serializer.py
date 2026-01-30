from rest_framework import serializers, validators
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

    outro_recurso_periodo = serializers.SlugRelatedField(
        queryset=OutroRecursoPeriodoPaa.objects.all(),
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
            'saldo_custeio', 'saldo_capital', 'saldo_livre'
        )
        read_only_fields = (
            'uuid', 'criado_em', 'alterado_em'
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ReceitaPrevistaOutroRecursoPeriodo.objects.all(),
                fields=['paa', 'outro_recurso_periodo'],
                message="Já existe uma receita cadastrada para o recurso no período!"
            ),
        ]
        ordering = ('outro_recurso_periodo__outro_recurso__nome',)

    def validate(self, attrs):
        paa = attrs.get('paa') or (self.instance.paa if self.instance else None)
        
        if paa:
            # Bloqueia edição quando o documento final foi gerado
            documento_final = paa.documento_final
            if documento_final and documento_final.concluido:
                raise serializers.ValidationError({
                    'mensagem': 'Não é possível editar receitas previstas de outros recursos após a geração do documento final do PAA.'
                })
        
        return super().validate(attrs)
