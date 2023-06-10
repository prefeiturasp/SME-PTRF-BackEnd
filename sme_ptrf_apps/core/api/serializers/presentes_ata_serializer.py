from rest_framework import serializers
from ...models import Ata, PresenteAta


class PresentesAtaSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Ata.objects.all()
    )

    def editavel(self, obj):
        return obj.editavel

    class Meta:
        model = PresenteAta
        fields = ('ata', 'identificacao', 'nome', 'cargo', 'membro', 'editavel', 'presente')


class PresentesAtaCreateSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Ata.objects.all()
    )

    class Meta:
        model = PresenteAta
        fields = ('ata', 'identificacao', 'nome', 'cargo', 'membro', 'presente')
