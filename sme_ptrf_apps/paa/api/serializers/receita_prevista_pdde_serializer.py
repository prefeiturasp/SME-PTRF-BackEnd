from rest_framework import serializers

from sme_ptrf_apps.paa.models import ReceitaPrevistaPdde, AcaoPdde, Paa


class ReceitaPrevistaPddeSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    acao_pdde = serializers.SlugRelatedField(queryset=AcaoPdde.objects.all(), slug_field='uuid')
    acao_pdde_objeto = serializers.SerializerMethodField()

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
                  )
        read_only_fields = ('uuid', 'paa', 'acao_pdde_objeto', 'criado_em', 'alterado_em')

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
                    'mensagem': 'Não é possível editar receitas previstas PDDE após a geração do documento final do PAA.'
                })
        
        return super().validate(attrs)


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
