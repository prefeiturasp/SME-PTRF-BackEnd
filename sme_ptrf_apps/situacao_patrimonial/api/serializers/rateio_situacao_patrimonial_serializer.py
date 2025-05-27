from rest_framework import serializers

from django.db.models import Sum

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoSerializer
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.despesas.api.serializers.tipo_custeio_serializer import TipoCusteioSerializer
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoRateio

class RateioSituacaoPatrimonialSerializer(serializers.ModelSerializer):
    conta_associacao = ContaAssociacaoSerializer()
    acao_associacao = AcaoAssociacaoSerializer()
    especificacao_material_servico = EspecificacaoMaterialServicoSerializer()
    valor_disponivel = serializers.SerializerMethodField()
    valor_utilizado = serializers.SerializerMethodField('get_valor_utilizado')
    tipo_documento_nome = serializers.SerializerMethodField('get_tipo_documento_nome')

    class Meta:
        model = RateioDespesa
        fields = ['valor_disponivel', 'valor_rateio', 'valor_utilizado', 'aplicacao_recurso',
                  'conta_associacao', 'acao_associacao', 'especificacao_material_servico', 'tipo_documento_nome']

    def _get_total_utilizado(self, rateio):
        cache_attr = f'_total_utilizado_{rateio.pk}'
        if not hasattr(self, cache_attr):
            total = BemProduzidoRateio.objects.filter(rateio=rateio).aggregate(
                total=Sum('valor_utilizado')
            )['total'] or 0
            setattr(self, cache_attr, total)
        return getattr(self, cache_attr)

    def get_valor_utilizado(self, rateio):
        return self._get_total_utilizado(rateio)

    def get_valor_disponivel(self, rateio):
        return rateio.valor_rateio - self._get_total_utilizado(rateio)

    def get_tipo_documento_nome(self, rateio):
        return rateio.despesa.tipo_documento.nome if rateio.despesa.tipo_documento else ''
