from rest_framework import serializers

from django.db.models import Sum
from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.despesas.models.despesa import Despesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa, BemProduzidoRateio
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_despesa_serializer import BemProduzidoDespesaSerializer
from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico


class BemProduzidoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    especificacao_do_bem = EspecificacaoMaterialServicoSerializer(read_only=True)
    despesas = serializers.SerializerMethodField()

    class Meta:
        model = BemProduzido
        fields = ('uuid','associacao', 'num_processo_incorporacao', 'quantidade', 'valor_individual', 'status', 'despesas', 'especificacao_do_bem')
        read_only_fields = ['despesas']
        
    def get_despesas(self, obj):
        despesas = obj.despesas.all()
        serializer = BemProduzidoDespesaSerializer(
            despesas, 
            many=True,
            context={'bem_produzido_uuid': obj.uuid}
        )
        return serializer.data
        
class RateioUpdateSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    valor_utilizado = serializers.DecimalField(max_digits=12, decimal_places=2)

class BemProduzidoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    especificacao_do_bem = serializers.SlugRelatedField(queryset=EspecificacaoMaterialServico.objects.all(), slug_field='uuid', required=False, allow_null=True)
    despesas = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    rateios = RateioUpdateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = BemProduzido
        fields = (
            'uuid',
            'associacao',
            'num_processo_incorporacao',
            'quantidade',
            'valor_individual',
            'especificacao_do_bem',
            'despesas',
            'rateios'
        )

    def create(self, validated_data):
        validated_data.pop('id', None)
        despesas_uuids = validated_data.pop('despesas', [])

        bem_produzido = BemProduzido.objects.create(
            status='INCOMPLETO',
            **validated_data
        )

        despesas = Despesa.objects.filter(uuid__in=despesas_uuids)

        for despesa in despesas:
            bem_produzido_despesa = BemProduzidoDespesa.objects.create(
                bem_produzido=bem_produzido,
                despesa=despesa
            )
            
            rateios = despesa.rateios.all()

            for rateio in rateios:
                BemProduzidoRateio.objects.create(
                    bem_produzido_despesa=bem_produzido_despesa,
                    rateio=rateio,
                    valor_utilizado=0
                )

        return bem_produzido
    
    from django.db.models import Sum

    def update(self, instance, validated_data):
        rateios_data = validated_data.pop('rateios', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for rateio_info in rateios_data:
            try:
                rateio_instance = BemProduzidoRateio.objects.get(uuid=rateio_info['uuid'])

                total_utilizado = BemProduzidoRateio.objects.filter(
                    rateio=rateio_instance.rateio
                ).exclude(uuid=rateio_instance.uuid).aggregate(
                    total=Sum('valor_utilizado')
                )['total'] or 0

                valor_disponivel = rateio_instance.rateio.valor_rateio - total_utilizado

                if rateio_info['valor_utilizado'] > valor_disponivel:
                    raise serializers.ValidationError(
                        f"O valor utilizado ({rateio_info['valor_utilizado']}) excede o valor disponível ({valor_disponivel}) para o rateio {rateio_info['uuid']}."
                    )

                rateio_instance.valor_utilizado = rateio_info['valor_utilizado']
                rateio_instance.save()
            except BemProduzidoRateio.DoesNotExist:
                raise serializers.ValidationError(f"BemProduzidoRateio com UUID {rateio_info['uuid']} não encontrado.")

        return instance
