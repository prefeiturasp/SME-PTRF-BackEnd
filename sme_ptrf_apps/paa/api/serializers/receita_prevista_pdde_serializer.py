from rest_framework import serializers
from django.db import transaction
from sme_ptrf_apps.paa.models import ReceitaPrevistaPdde, AcaoPdde, Paa


class ReceitaPrevistaPddeSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    acao_pdde = serializers.SlugRelatedField(queryset=AcaoPdde.objects.all(), slug_field='uuid')
    acao_pdde_objeto = serializers.SerializerMethodField()
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    def get_acao_pdde_objeto(self, obj):
        if obj.acao_pdde:
            programa = {
                'uuid': str(obj.acao_pdde.programa.uuid),
                'nome': obj.acao_pdde.programa.nome,
            }
            return {
                'uuid': obj.acao_pdde.uuid,
                'nome': obj.acao_pdde.nome,
                'programa_objeto': programa,
            }
        return None

    class Meta:
        model = ReceitaPrevistaPdde
        fields = ('uuid', 'paa', 'acao_pdde', 'acao_pdde_objeto',
                  'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre',
                  'saldo_capital', 'saldo_custeio', 'saldo_livre',
                  'confirmar_limpeza_prioridades_paa',
                  )
        read_only_fields = ('uuid', 'paa', 'acao_pdde_objeto', 'criado_em', 'alterado_em',
                            'confirmar_limpeza_prioridades_paa',
                            )

    def validate(self, attrs):
        if not attrs.get('acao_pdde') and not self.instance:
            raise serializers.ValidationError({'acao_pdde': 'O campo Ação PDDE é obrigatório.'})
        if not attrs.get('paa') and not self.instance:
            raise serializers.ValidationError({'paa': 'PAA não informado.'})

        paa = attrs.get('paa') or (self.instance.paa if self.instance else None)

        # Resolve paa if it's a string (UUID) to the actual Paa object
        if paa and isinstance(paa, str):
            try:
                paa = Paa.objects.get(uuid=paa)
            except Paa.DoesNotExist:
                # If paa doesn't exist, skip the documento_final check
                # The field validation will handle the error
                paa = None

        if paa:
            # Bloqueia edição quando o documento final foi gerado
            documento_final = paa.documento_final
            if documento_final and documento_final.concluido:
                raise serializers.ValidationError({
                    'mensagem': (
                        'Não é possível editar receitas previstas PDDE após a geração do documento final do PAA.')
                })

        # Verifica prioridades do PAA impactadas
        self._verificar_prioridades_paa_impactadas(attrs, self.instance)
        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs, instance) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPDDEService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(attrs, instance)
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
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPDDEService

        service = PrioridadesPaaImpactadasReceitasPrevistasPDDEService(receita_prevista_attrs, instance_despesa)
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


class ReceitasPrevistasPDDEValoresSerializer(serializers.ModelSerializer):
    previsao_valor_custeio = serializers.FloatField(read_only=True)
    previsao_valor_capital = serializers.FloatField(read_only=True)
    previsao_valor_livre = serializers.FloatField(read_only=True)
    saldo_custeio = serializers.FloatField(read_only=True)
    saldo_capital = serializers.FloatField(read_only=True)
    saldo_livre = serializers.FloatField(read_only=True)

    class Meta:
        model = ReceitaPrevistaPdde
        fields = (
            'uuid',
            'previsao_valor_custeio', 'previsao_valor_capital', 'previsao_valor_livre',
            'saldo_custeio', 'saldo_capital', 'saldo_livre')
        read_only_fields = (
            'uuid',
            'previsao_valor_custeio', 'previsao_valor_capital', 'previsao_valor_livre',
            'saldo_custeio', 'saldo_capital', 'saldo_livre')
