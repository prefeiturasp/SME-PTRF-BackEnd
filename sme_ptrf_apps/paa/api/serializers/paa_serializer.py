from rest_framework import serializers

from sme_ptrf_apps.paa.models import Paa, PeriodoPaa, ObjetivoPaa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.services import PaaService
from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer

from . import PeriodoPaaSerializer


class ObjetivoPaaUpdateSerializer(serializers.Serializer):
    objetivo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=ObjetivoPaa.objects.all()
    )
    nome = serializers.CharField(required=False)
    _destroy = serializers.BooleanField(required=False, default=False)


class PaaSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(queryset=Associacao.objects.all(), slug_field='uuid')
    periodo_paa_objeto = PeriodoPaaSerializer(read_only=True, many=False)
    objetivos = ObjetivoPaaSerializer(many=True, read_only=True)

    class Meta:
        model = Paa
        fields = ('uuid', 'periodo_paa', 'associacao', 'periodo_paa_objeto', 'saldo_congelado_em',
                  'texto_introducao', 'texto_conclusao', 'status', 'objetivos')
        read_only_fields = ('periodo_paa_objeto', 'periodo_paa', 'status', 'objetivos')

    def validate(self, attrs):
        try:
            PaaService.pode_elaborar_novo_paa()
        except Exception as exc:
            raise serializers.ValidationError({'non_field_errors': exc})

        periodo_paa = PeriodoPaa.periodo_vigente()
        if not periodo_paa:
            raise serializers.ValidationError({
                'non_field_errors': ['Nenhum Período vigente foi encontrado.']
            })
        attrs["periodo_paa"] = periodo_paa

        return super().validate(attrs)

    def create(self, validated_data):
        periodo_paa = validated_data.get('periodo_paa')  # obtido pelo Service, o Período vigente em validate()
        associacao = validated_data.get('associacao')  # obtido pelo payload

        existe_paa = Paa.objects.filter(periodo_paa=periodo_paa, associacao=associacao).exists()
        if existe_paa:
            raise serializers.ValidationError({
                'non_field_errors': ['Já existe um PAA para a Associação informada.']
            })

        instance = super().create(validated_data)

        return instance


class PaaUpdateSerializer(serializers.ModelSerializer):
    objetivos = ObjetivoPaaUpdateSerializer(many=True)

    class Meta:
        model = Paa
        fields = [
            "texto_introducao",
            "texto_conclusao",
            "objetivos"
        ]

    def update(self, instance, validated_data):
        objetivos_data = validated_data.pop("objetivos", None)

        instance = super().update(instance, validated_data)

        if objetivos_data is not None:
            self._generenciar_objetivos(instance, objetivos_data)

        return instance

    def _generenciar_objetivos(self, paa, objetivos_data):
        current_objetivos_ids = []

        for objetivo_input in objetivos_data:
            if "objetivo" in objetivo_input:
                objetivo = objetivo_input.get("objetivo")

                if objetivo_input.get('_destroy'):
                    objetivo.delete()
                    continue

                if paa == objetivo.paa:
                    objetivo.nome = objetivo_input["nome"]
                    print(objetivo_input["nome"])
                    objetivo.save(update_fields=['nome'])

                paa.objetivos.add(objetivo)
                current_objetivos_ids.append(objetivo.id)

            elif "nome" in objetivo_input:
                objetivo = ObjetivoPaa.objects.create(
                    nome=objetivo_input["nome"],
                    paa=paa
                )
                paa.objetivos.add(objetivo)
                current_objetivos_ids.append(objetivo.id)

        paa.objetivos.set(current_objetivos_ids)
