from rest_framework import serializers

from ...models import MotivoAprovacaoRessalva


class MotivoAprovacaoRessalvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivoAprovacaoRessalva
        fields = ('id', 'uuid', 'motivo')


    def create(self, validated_data):
        motivo = validated_data.get('motivo')

        if MotivoAprovacaoRessalva.objects.filter(motivo=motivo).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de aprovação de PC com ressalva já existe.'
                })

        instance = super().create(validated_data)
        return instance


    def update(self, instance, validated_data):
        motivo = validated_data.get('motivo')

        if MotivoAprovacaoRessalva.objects.filter(motivo=motivo).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Este motivo de aprovação de PC com ressalva já existe.'
                })

        instance = super().update(instance, validated_data)
        return instance
