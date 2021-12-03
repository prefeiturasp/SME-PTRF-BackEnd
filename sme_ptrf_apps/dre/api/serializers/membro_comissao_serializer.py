from rest_framework import serializers

from sme_ptrf_apps.core.models import Unidade

from ...models import MembroComissao


class MembroComissaoSerializer(serializers.ModelSerializer):
    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.dres.all()
    )

    class Meta:
        model = MembroComissao
        fields = ('uuid', 'rf', 'nome', 'email', 'qtd_comissoes', 'dre')
