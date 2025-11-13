from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa


class PresentesAtaPaaSerializer(serializers.ModelSerializer):
    ata_paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaPaa.objects.all()
    )

    def editavel(self, obj):
        return obj.editavel

    class Meta:
        model = ParticipanteAtaPaa
        fields = ('ata_paa', 'identificacao', 'nome', 'cargo', 'membro', 'editavel', 'presente', 'conselho_fiscal', 'professor_gremio')


class PresentesAtaPaaCreateSerializer(serializers.ModelSerializer):
    ata_paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaPaa.objects.all()
    )
    
    presidente_da_reuniao = serializers.BooleanField(required=False, allow_null=True)
    secretario_da_reuniao = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, attrs):
        """
        Valida que professor do grêmio não pode ser presidente nem secretário.
        """
        professor_gremio = attrs.get('professor_gremio', False)
        presidente = attrs.get('presidente_da_reuniao', False)
        secretario = attrs.get('secretario_da_reuniao', False)

        if professor_gremio and (presidente or secretario):
            raise serializers.ValidationError({
                'professor_gremio': 'O professor do grêmio não pode ser presidente nem secretário da reunião.'
            })

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            presidente = validated_data.pop('presidente_da_reuniao', False)
            secretario = validated_data.pop('secretario_da_reuniao', False)
            
            participante = ParticipanteAtaPaa.objects.create(**validated_data)
            
            if participante.ata_paa:
                if presidente:
                    participante.ata_paa.presidente_da_reuniao = participante
                    participante.ata_paa.save(update_fields=['presidente_da_reuniao'])
                elif secretario:
                    participante.ata_paa.secretario_da_reuniao = participante
                    participante.ata_paa.save(update_fields=['secretario_da_reuniao'])
            
            return participante

    def update(self, instance, validated_data):
        with transaction.atomic():
            presidente = validated_data.pop('presidente_da_reuniao', False)
            secretario = validated_data.pop('secretario_da_reuniao', False)
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            if instance.ata_paa:
                if presidente:
                    instance.ata_paa.presidente_da_reuniao = instance
                    instance.ata_paa.save(update_fields=['presidente_da_reuniao'])
                elif secretario:
                    instance.ata_paa.secretario_da_reuniao = instance
                    instance.ata_paa.save(update_fields=['secretario_da_reuniao'])
            
            return instance

    class Meta:
        model = ParticipanteAtaPaa
        fields = ('ata_paa', 'identificacao', 'nome', 'cargo', 'membro', 'presente', 'presidente_da_reuniao', 'secretario_da_reuniao', 'conselho_fiscal', 'professor_gremio')

