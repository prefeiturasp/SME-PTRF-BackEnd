from rest_framework import serializers
from ...models import Ata, Participante


class PresentesAtaSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Ata.objects.all()
    )

    def editavel(self, obj):
        return obj.editavel

    class Meta:
        model = Participante
        fields = ('ata', 'identificacao', 'nome', 'cargo', 'membro', 'editavel', 'presente', 'professor_gremio')


class PresentesAtaCreateSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Ata.objects.all()
    )

    data_inicio_no_cargo = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=['%d/%m/%Y', 'iso-8601']
    )
    vago = serializers.BooleanField(required=False, default=False)

    presidente_da_reuniao = serializers.BooleanField(required=False, allow_null=True)
    secretario_da_reuniao = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        model = Participante
        fields = ('ata', 'identificacao', 'nome', 'cargo', 'data_inicio_no_cargo', 'vago', 'membro', 'presente', 'presidente_da_reuniao',
                  'secretario_da_reuniao', 'professor_gremio')
