from rest_framework import serializers

from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa, Paa
from sme_ptrf_apps.core.models import AcaoAssociacao


class ReceitaPrevistaPaaSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    acao_associacao = serializers.SlugRelatedField(queryset=AcaoAssociacao.objects.all(), slug_field='uuid')
    acao_associacao_objeto = serializers.SerializerMethodField()

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
                  'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre')
        read_only_fields = ('uuid', 'acao_associacao_objeto', 'criado_em', 'alterado_em')

    def validate(self, attrs):
        if not attrs.get('paa') and not self.instance:
            # Valida se paa foi informada no create
            raise serializers.ValidationError({'paa': 'O campo PAA é obrigatório.'})

        if not attrs.get('acao_associacao') and not self.instance:
            # Valida se acao_associacao foi informada no create
            raise serializers.ValidationError({'acao_associacao': 'O campo Ação de Associação é obrigatório.'})
        return super().validate(attrs)
