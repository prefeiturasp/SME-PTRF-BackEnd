from rest_framework import serializers
from ...models import AtaParecerTecnico, PresenteAtaDre


class PresentesAtaDreSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaParecerTecnico.objects.all()
    )

    def editavel(self, obj):
        return obj.editavel

    class Meta:
        model = PresenteAtaDre
        fields = ('ata', 'rf', 'nome', 'cargo', 'editavel',)


class PresentesAtaDreCreateSerializer(serializers.ModelSerializer):
    ata = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaParecerTecnico.objects.all()
    )

    class Meta:
        model = PresenteAtaDre
        fields = ('ata', 'rf', 'nome', 'cargo',)
