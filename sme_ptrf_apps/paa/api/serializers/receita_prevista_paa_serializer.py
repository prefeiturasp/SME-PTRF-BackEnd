from rest_framework import serializers
from django.db import transaction
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa, Paa
from sme_ptrf_apps.core.models import AcaoAssociacao


class ReceitaPrevistaPaaSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    acao_associacao = serializers.SlugRelatedField(queryset=AcaoAssociacao.objects.all(), slug_field='uuid')
    acao_associacao_objeto = serializers.SerializerMethodField()
    confirmar_limpeza_prioridades_paa = serializers.BooleanField(
        required=False,
        default=False,
        write_only=True,
        help_text='Se True, confirma a limpeza do valor das prioridades do PAA impactadas.'
    )

    def get_acao_associacao_objeto(self, obj):
        if obj.acao_associacao:
            acao = {
                'uuid': str(obj.acao_associacao.acao.uuid),
                'id': obj.acao_associacao.acao.id,
                'nome': obj.acao_associacao.acao.nome,
            }
            return {
                'uuid': obj.acao_associacao.uuid,
                'id': obj.acao_associacao.id,
                'acao_id': obj.acao_associacao.acao_id,
                'associacao_id': obj.acao_associacao.associacao_id,
                'status': obj.acao_associacao.status,
                'acao_objeto': acao,
            }
        return None

    class Meta:
        model = ReceitaPrevistaPaa
        fields = ('id', 'uuid', 'paa', 'acao_associacao', 'acao_associacao_objeto',
                  'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre',
                  'saldo_congelado_custeio', 'saldo_congelado_capital', 'saldo_congelado_livre',
                  'confirmar_limpeza_prioridades_paa')
        read_only_fields = ('uuid', 'saldo_congelado_custeio', 'saldo_congelado_capital',
                            'saldo_congelado_livre', 'acao_associacao_objeto', 'criado_em', 'alterado_em',
                            'confirmar_limpeza_prioridades_paa')

    def validate(self, attrs):
        if not attrs.get('paa') and not self.instance:
            # Valida se paa foi informada no create
            raise serializers.ValidationError({'paa': 'O campo PAA é obrigatório.'})

        if not attrs.get('acao_associacao') and not self.instance:
            # Valida se acao_associacao foi informada no create
            raise serializers.ValidationError({'acao_associacao': 'O campo Ação de Associação é obrigatório.'})

        paa = attrs.get('paa') or (self.instance.paa if self.instance else None)

        if paa:
            # Bloqueia edição quando o documento final foi gerado
            documento_final = paa.documento_final
            if documento_final and documento_final.concluido:
                raise serializers.ValidationError({
                    'mensagem': 'Não é possível editar receitas previstas após a geração do documento final do PAA.'
                })

        # Verifica prioridades do PAA impactadas
        self._verificar_prioridades_paa_impactadas(attrs, self.instance)

        return super().validate(attrs)

    def _verificar_prioridades_paa_impactadas(self, attrs, instance) -> list:
        """
        Verifica se há prioridades do PAA que serão impactadas.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService

        confirmar_limpeza = attrs.get('confirmar_limpeza_prioridades_paa', False)

        prioridades_impactadas = []
        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(attrs, instance)
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
        Limpa o valor_total das prioridades do PAA impactadas pelos rateios da despesa.
        """
        from sme_ptrf_apps.paa.services import PrioridadesPaaImpactadasReceitasPrevistasPTRFService

        service = PrioridadesPaaImpactadasReceitasPrevistasPTRFService(receita_prevista_attrs, instance_despesa)
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
