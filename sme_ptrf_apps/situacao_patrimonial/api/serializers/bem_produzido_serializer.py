from rest_framework import serializers

from sme_ptrf_apps.despesas.api.serializers.especificacao_material_servico_serializer import EspecificacaoMaterialServicoSerializer
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.situacao_patrimonial.api.serializers.bem_produzido_despesa_serializer import BemProduzidoDespesaSerializer, Despesa 
from sme_ptrf_apps.despesas.models import EspecificacaoMaterialServico


class BemProduzidoSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    especificacao_do_bem = EspecificacaoMaterialServicoSerializer(read_only=True)
    despesas = BemProduzidoDespesaSerializer(read_only=True, many=True)

    class Meta:
        model = BemProduzido
        fields = ('uuid','associacao', 'num_processo_incorporacao', 'quantidade', 'valor_individual', 'status', 'despesas', 'especificacao_do_bem')
        read_only_fields = ['despesas']

class BemProduzidoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    especificacao_do_bem = serializers.SlugRelatedField(queryset=EspecificacaoMaterialServico.objects.all(), slug_field='uuid', required=False, allow_null=True)
    despesas = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

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

        return bem_produzido
    
    def update(self, instance, validated_data):
        despesas_uuids = validated_data.pop('despesas', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if despesas_uuids is not None:
            BemProduzidoDespesa.objects.filter(bem_produzido=instance).delete()

            despesas = Despesa.objects.filter(uuid__in=despesas_uuids)
            for despesa in despesas:
                BemProduzidoDespesa.objects.create(
                    bem_produzido=instance,
                    despesa=despesa
                )

        return instance
