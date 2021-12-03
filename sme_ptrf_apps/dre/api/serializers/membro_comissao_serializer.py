from rest_framework import serializers

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.dre.api.serializers.comissao_serializer import ComissaoSerializer

from ...models import MembroComissao


class MembroComissaoListSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')


class MembroComissaoCreateSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')


class MembroComissaoRetrieveSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeLookUpSerializer
    dre = UnidadeLookUpSerializer()
    comissoes = ComissaoSerializer(many=True)

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre', 'comissoes')
