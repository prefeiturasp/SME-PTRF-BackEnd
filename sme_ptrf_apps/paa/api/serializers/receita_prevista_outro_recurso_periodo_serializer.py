from django.db import transaction
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
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    class Meta:
        model = ReceitaPrevistaOutroRecursoPeriodo
        fields = (
            'uuid', 'paa', 'outro_recurso_periodo',
            'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre',
            'saldo_custeio', 'saldo_capital', 'saldo_livre',
            'confirmar_limpeza_prioridades_paa',
        )
        read_only_fields = (
            'uuid', 'criado_em', 'alterado_em',
            'confirmar_limpeza_prioridades_paa',
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

        self._verificar_prioridades_paa_impactadas(attrs, self.instance)
        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs, instance) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(attrs, instance)
        prioridades = service.verificar_prioridades_impactadas()
        prioridades_impactadas.extend(prioridades)

        if prioridades_impactadas and not confirmar_limpeza:
            raise serializers.ValidationError({
                "confirmar": (
                    "Existem prioridades cadastradas que utilizam o valor da receita prevista. "
                    "O valor total será removido das prioridades cadastradas e é necessário revisá-las para "
                    "alterar o valor total.")
            })

    def _limpar_prioridades_paa(self, receita_prevista_attrs, instance_despesa):
        """
        Limpa o valor_total das prioridades do PAA impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService

        service = PrioridadesPaaImpactadasReceitasPrevistasOutroRecursoPeriodoService(
            receita_prevista_attrs, instance_despesa)
        service.limpar_valor_prioridades_impactadas()

    @transaction.atomic
    def update(self, instance, validated_data):
        # Remove flag de confirmação do validated_data (não é campo do model)
        confirmar_limpeza_prioridades = validated_data.pop('confirmar_limpeza_prioridades_paa', False)

        # Limpa prioridades do PAA se confirmado, com dados e instance antes de salvar
        if confirmar_limpeza_prioridades:
            self._limpar_prioridades_paa(validated_data, instance)

        return super().update(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop('confirmar_limpeza_prioridades_paa', False)
        return super().create(validated_data)
