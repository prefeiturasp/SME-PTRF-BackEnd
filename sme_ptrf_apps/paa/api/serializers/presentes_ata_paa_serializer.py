from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa


class PresentesAtaPaaSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por serializar os dados dos presentes
    na ata do PAA.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    ata_paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaPaa.objects.all()
    )
    secretario_da_reuniao = serializers.SerializerMethodField()

    def editavel(self, obj: ParticipanteAtaPaa) -> bool:
        """
        Retorna se o participante da ata do PAA é editavel.

        Args:
            obj (ParticipanteAtaPaa): Instância do Participante da ata do PAA.

        Returns:
            bool: se é editavel.
        """
        return obj.editavel

    def get_secretario_da_reuniao(self, obj: ParticipanteAtaPaa) -> bool:
        """
        Retorna o secretário da reunião.

        Args:
            obj (ParticipanteAtaPaa): Instância do Participante da ata do PAA.

        Returns:
            bool: É ou não o secretário da reunião.
        """
        if obj.ata_paa and obj.ata_paa.secretario_da_reuniao == obj:
            return True
        return False

    class Meta:
        model = ParticipanteAtaPaa
        fields = ('ata_paa', 'identificacao', 'nome', 'cargo', 'membro', 'editavel', 'presente', 'conselho_fiscal',
                  'professor_gremio', 'secretario_da_reuniao')


class PresentesAtaPaaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer responsável por validar, criar, atualizar e serializar
    os dados de um PAA.

    Além dos campos do modelo, expõe campos calculados para apresentação.
    """
    ata_paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=AtaPaa.objects.all()
    )

    presidente_da_reuniao = serializers.BooleanField(required=False, allow_null=True)
    secretario_da_reuniao = serializers.BooleanField(required=False, allow_null=True)

    def validate(self, attrs: dict) -> dict:
        """
        Valida os dados para criação de um PAA.

        Ainda não possui validações.

        Args:
            attrs (dict): Dados informados do participante da ata Paa.

        Returns:
            dict: Dados informados do participante da ata Paa.

        """
        return attrs

    def create(self, validated_data: dict) -> ParticipanteAtaPaa:
        """
        Cria uma nova instância do participante da Ata do Paa.

        Após a criação verifica se presidente ou secretário
        adiciona a informação

        Args:
            validated_data (dict): Dados validados para criação do PAA.

        Returns:
            Paa: Instância do PAA criada.

        """
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

    def update(self, instance: ParticipanteAtaPaa, validated_data: dict) -> ParticipanteAtaPaa:
        """
        Atualiza uma nova instância do participante da Ata PAA.

        Além de atualizar os dados normais ele verifica se é
        presidente ou sercretário e salva a informação.

        Args:
            instance (ParticipanteAtaPaa): instânciaa do modelo ParticipanteAtaPaa
            validated_data (dict): Dados validados para atualização
            do participante da ata do PAA.

        Returns:
            ParticipanteAtaPaa: Instância do participante PAA atualizada.

        """
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
        fields = ('uuid', 'ata_paa', 'identificacao', 'nome', 'cargo', 'membro', 'presente', 'presidente_da_reuniao',
                  'secretario_da_reuniao', 'conselho_fiscal', 'professor_gremio')
