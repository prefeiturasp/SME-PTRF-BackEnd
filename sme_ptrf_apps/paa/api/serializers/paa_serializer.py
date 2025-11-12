from django.db import transaction
from django.db import IntegrityError
from rest_framework import serializers
from sme_ptrf_apps.paa.models import Paa, PeriodoPaa, ObjetivoPaa, AtividadeEstatutaria, AtividadeEstatutariaPaa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.services import PaaService
from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer, ObjetivoPaaUpdateSerializer
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_paa_serializer import AtividadeEstatutariaPaaSerializer, AtividadeEstaturariaPaaUpdateSerializer
from sme_ptrf_apps.paa.api.serializers import PeriodoPaaSerializer


class AtividadesPrevistasPaaDetailSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import RecursoProprioPaaListSerializer

    atividades_estatutarias = AtividadeEstatutariaPaaSerializer(
        source='atividadeestatutariapaa_set',
        many=True,
        read_only=True
    )
    recursos_proprios = RecursoProprioPaaListSerializer(
        source='recursopropriopaa_set',
        many=True,
        read_only=True
    )

    total_recursos_proprios = serializers.SerializerMethodField()

    class Meta:
        model = Paa
        fields = ('atividades_estatutarias', 'recursos_proprios', 'total_recursos_proprios', )
        read_only_fields = ('atividades_estatutarias', 'recursos_proprios', 'total_recursos_proprios', )

    def get_total_recursos_proprios(self, obj):
        return obj.get_total_recursos_proprios()


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
    atividades_estatutarias = AtividadeEstaturariaPaaUpdateSerializer(
        many=True,
        write_only=True
    )
    atividades_estatutarias_paa = AtividadeEstatutariaPaaSerializer(
        source='atividadeestatutariapaa_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Paa
        fields = [
            "texto_introducao",
            "texto_conclusao",
            "objetivos",
            "atividades_estatutarias",
            "atividades_estatutarias_paa"
        ]

    def update(self, instance, validated_data):
        objetivos_data = validated_data.pop("objetivos", None)
        atividades_estatutarias_data = validated_data.pop("atividades_estatutarias", None)

        instance = super().update(instance, validated_data)

        if objetivos_data is not None:
            self._generenciar_objetivos(instance, objetivos_data)

        if atividades_estatutarias_data is not None:
            self._gerenciar_atividades_estatutarias(instance, atividades_estatutarias_data)

        return instance

    def _generenciar_objetivos(self, paa, objetivos_data):
        with transaction.atomic():
            current_objetivos_ids = []

            for objetivo_input in objetivos_data:
                if "objetivo" in objetivo_input:
                    objetivo = objetivo_input.get("objetivo")

                    if objetivo_input.get('_destroy'):
                        objetivo.delete()
                        continue

                    if paa == objetivo.paa:
                        objetivo.nome = objetivo_input["nome"]
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

    def _gerenciar_atividades_estatutarias(self, paa, atividades_data):
        with transaction.atomic():

            for item in atividades_data:
                atividade = item.get("atividade_estatutaria")
                nome = item.get("nome")
                tipo = item.get("tipo")
                data = item.get("data")
                destroy = item.get("_destroy", False)

                mes = data.month if data else None

                if atividade:

                    if atividade.paa == paa:

                        if destroy:
                            AtividadeEstatutariaPaa.objects.filter(atividade_estatutaria=atividade).delete()
                            atividade.delete()
                            continue

                        if nome or tipo:
                            if nome:
                                atividade.nome = nome
                            if tipo:
                                atividade.tipo = tipo
                            if mes:
                                atividade.mes = mes

                            atividade.save()

                    else:
                        if destroy:
                            raise serializers.ValidationError(
                                {"mensagem": "Não é possível excluir atividade estatutária que não pertece ao PAA."})

                    atividade_paa, created = AtividadeEstatutariaPaa.objects.get_or_create(
                        atividade_estatutaria=atividade,
                        paa=paa,
                        defaults={"data": data}
                    )

                    if not created and data:
                        atividade_paa.data = data
                        atividade_paa.save()

                    continue

                if not nome or not tipo or not data:
                    raise serializers.ValidationError({"mensagem": "Nova atividade precisa de nome, tipo e data."})

                try:
                    nova_atividade = AtividadeEstatutaria.objects.create(
                        nome=nome,
                        tipo=tipo,
                        mes=mes,
                        paa=paa
                    )
                except IntegrityError:
                    raise serializers.ValidationError(
                        {"mensagem": "Já existe uma atividade com esse nome, mês e tipo."})

                try:
                    AtividadeEstatutariaPaa.objects.create(
                        atividade_estatutaria=nova_atividade,
                        paa=paa,
                        data=data
                    )
                except IntegrityError:
                    raise serializers.ValidationError(
                        {"mensagem": "Já existe uma atividade paa com esse paa e data."})
