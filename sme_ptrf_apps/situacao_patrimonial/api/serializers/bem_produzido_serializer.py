from decimal import Decimal
from rest_framework import serializers

from django.db.models import Sum
from sme_ptrf_apps.despesas.models.despesa import Despesa
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa, BemProduzidoItem, BemProduzidoRateio
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_despesa_serializer import BemProduzidoDespesaSerializer
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_item_serializer import BemProduzidoItemSerializer


class BemProduzidoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    despesas = serializers.SerializerMethodField()
    items = BemProduzidoItemSerializer(many=True)

    class Meta:
        model = BemProduzido
        fields = ('uuid', 'associacao', 'status', 'despesas', 'items')
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
    uuid = serializers.SlugRelatedField(queryset=RateioDespesa.objects.all(), slug_field='uuid')
    bem_produzido_despesa = serializers.SlugRelatedField(queryset=BemProduzidoDespesa.objects.all(), slug_field='uuid')
    valor_utilizado = serializers.DecimalField(max_digits=12, decimal_places=2)


class RecursoProprioSerializer(serializers.Serializer):
    valor_recurso_proprio_utilizado = serializers.DecimalField(max_digits=10, decimal_places=2)
    bem_produzido_despesa = serializers.UUIDField()


class BemProduzidoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')

    despesas = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    rateios = RateioUpdateSerializer(many=True, write_only=True, required=False)

    recurso_proprio = RecursoProprioSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = BemProduzido
        fields = (
            'uuid',
            'associacao',
            'despesas',
            'rateios',
            'recurso_proprio'
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
            BemProduzidoDespesa.objects.create(
                bem_produzido=bem_produzido,
                despesa=despesa
            )

        BemProduzidoItem.objects.create(
            valor_individual=None,
            quantidade=None,
            num_processo_incorporacao='',
            especificacao_do_bem=None,
            bem_produzido=bem_produzido,
        )

        return bem_produzido

    from django.db.models import Sum

    def update(self, instance, validated_data):
        rateios_data = validated_data.pop('rateios', [])
        recursos_proprios_data = validated_data.pop('recurso_proprio', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for rateio_info in rateios_data:
            try:
                rateio_instance, _ = BemProduzidoRateio.objects.get_or_create(
                    rateio=rateio_info['uuid'],
                    bem_produzido_despesa=rateio_info['bem_produzido_despesa']
                )

                total_utilizado = BemProduzidoRateio.objects.filter(
                    rateio=rateio_instance.rateio
                ).exclude(uuid=rateio_instance.uuid).aggregate(
                    total=Sum('valor_utilizado')
                )['total'] or 0

                valor_disponivel = rateio_instance.rateio.valor_rateio - total_utilizado

                if Decimal(str(rateio_info['valor_utilizado'])) > valor_disponivel:
                    raise serializers.ValidationError(
                        f"O valor utilizado ({rateio_info['valor_utilizado']}) excede o valor disponível ({valor_disponivel}) para o rateio {rateio_info['uuid']}."
                    )

                rateio_instance.valor_utilizado = rateio_info['valor_utilizado']
                rateio_instance.save()
            except BemProduzidoRateio.DoesNotExist:
                raise serializers.ValidationError(f"BemProduzidoRateio com UUID {rateio_info['uuid']} não encontrado.")

        for recurso_data in recursos_proprios_data:
            try:
                bem = BemProduzidoDespesa.objects.get(uuid=recurso_data['bem_produzido_despesa'])

                valor_a_utilizar = Decimal(str(recurso_data['valor_recurso_proprio_utilizado']))

                # Soma de todos os recursos próprios utilizados relacionados à mesma despesa, exceto este bem
                soma_outros = BemProduzidoDespesa.objects.filter(
                    despesa=bem.despesa
                ).exclude(uuid=bem.uuid).aggregate(
                    total=Sum('valor_recurso_proprio_utilizado')
                )['total'] or Decimal('0.00')

                valor_total_utilizado = soma_outros + valor_a_utilizar

                if valor_total_utilizado > bem.despesa.valor_recursos_proprios:
                    raise serializers.ValidationError(
                        f"O valor total de recurso próprio utilizado ({valor_total_utilizado}) excede o valor disponível "
                        f"({bem.despesa.valor_recursos_proprios}) para a despesa {bem.despesa.uuid}."
                    )

                bem.valor_recurso_proprio_utilizado = valor_a_utilizar
                bem.save()

            except BemProduzidoDespesa.DoesNotExist:
                raise serializers.ValidationError(
                    f"BemProduzidoDespesa com UUID {recurso_data['bem_produzido_despesa']} não encontrado."
                )

        return instance
