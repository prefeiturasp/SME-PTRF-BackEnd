from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoLookupSerializer
from sme_ptrf_apps.core.models import ProcessoAssociacao, Associacao


class ProcessoAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano',)

class ProcessoAssociacaoRetrieveSerializer(serializers.ModelSerializer):
    associacao = AssociacaoLookupSerializer()
    permite_exclusao = serializers.SerializerMethodField('get_permite_exclusao')
    tooltip_exclusao = serializers.SerializerMethodField('get_tooltip_exclusao')

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano', 'criado_em', 'alterado_em',
                  'permite_exclusao', 'tooltip_exclusao')

    def get_tooltip_exclusao(self, obj):
        if obj.e_o_ultimo_processo_do_ano_com_pcs_vinculada:
            return "Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo."
        else:
            return ""

    def get_permite_exclusao(self, obj):
        return not obj.e_o_ultimo_processo_do_ano_com_pcs_vinculada
