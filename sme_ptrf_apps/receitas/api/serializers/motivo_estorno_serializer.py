from rest_framework import serializers
from sme_ptrf_apps.core.models import Recurso
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...models import MotivoEstorno


class MotivoEstornoSerializer(serializers.ModelSerializer):

    recurso = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=Recurso.objects.all()
    )

    def create(self, validated_data):
        motivo = validated_data['motivo']
        motivo = ' '.join(motivo.split())
        recurso = validated_data.get('recurso', None)

        motivo_ja_cadastrado = MotivoEstorno.objects.filter(motivo__iexact=motivo, recurso=recurso).all()
        if motivo_ja_cadastrado:
            raise serializers.ValidationError({
                    'non_field_errors': ["Motivo já cadastrado para este recurso."]
                })

        motivo_estorno_criado = MotivoEstorno.objects.create(**validated_data)

        return motivo_estorno_criado

    def update(self, instance, validated_data):
        motivo = validated_data.get("motivo", None)
        motivo = ' '.join(motivo.split())
        recurso = validated_data.get("recurso", instance.recurso)

        if motivo and instance.motivo != motivo:
            motivo_ja_cadastrado = MotivoEstorno.objects.filter(motivo__iexact=motivo, recurso=recurso).all()
            if motivo_ja_cadastrado:
                raise serializers.ValidationError({
                    'non_field_errors': ["Motivo já cadastrado para este recurso."]
                })

        update_instance_from_dict(instance, validated_data, save=True)

        return instance

    class Meta:
        model = MotivoEstorno
        fields = ('id', 'uuid', 'motivo', 'recurso')
