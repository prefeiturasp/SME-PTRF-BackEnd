from rest_framework import serializers
from ...models import MotivoPagamentoAntecipado
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class MotivoPagamentoAntecipadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoPagamentoAntecipado
        fields = ('id', 'uuid', 'motivo')

    def create(self, validated_data):
        motivo = validated_data['motivo']
        motivo_ja_cadastrado = MotivoPagamentoAntecipado.objects.filter(motivo__iexact=motivo).exists()
        if motivo_ja_cadastrado:
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de pagamento antecipado já existe.'
                })

        tipo_documento_criado = MotivoPagamentoAntecipado.objects.create(**validated_data)
        return tipo_documento_criado

    def update(self, instance, validated_data):
        motivo = validated_data.get("motivo", None)

        if motivo and instance.motivo != motivo:
            motivo_ja_cadastrado = MotivoPagamentoAntecipado.objects.filter(motivo__iexact=motivo).exists()

            if motivo_ja_cadastrado:
                raise serializers.ValidationError(
                    {"non_field_errors": "Este motivo de pagamento antecipado já existe."}
                )

        update_instance_from_dict(instance, validated_data, save=True)

        return instance
