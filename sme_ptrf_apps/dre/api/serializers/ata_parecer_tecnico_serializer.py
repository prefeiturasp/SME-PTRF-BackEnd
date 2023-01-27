from rest_framework import serializers
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict
from ...models import AtaParecerTecnico
from sme_ptrf_apps.core.models import Periodo, Unidade
from ...api.serializers.presentes_ata_dre_serializer import PresentesAtaDreSerializer, PresentesAtaDreCreateSerializer
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.unidade_serializer import UnidadeLookUpSerializer


class AtaParecerTecnicoLookUpSerializer(serializers.ModelSerializer):
    alterado_em = serializers.SerializerMethodField('get_alterado_em')
    versao = serializers.SerializerMethodField('get_versao')

    def get_alterado_em(self, obj):
        return obj.preenchida_em

    def get_versao(self, obj):
        return 'FINAL' if obj.arquivo_pdf else 'PREVIA'

    class Meta:
        model = AtaParecerTecnico
        fields = (
            'uuid',
            'alterado_em',
            'status_geracao_pdf',
            'arquivo_pdf',
            'versao',
        )


class AtaParecerTecnicoSerializer(serializers.ModelSerializer):
    hora_reuniao = serializers.SerializerMethodField('get_hora_reuniao')

    alterado_em = serializers.SerializerMethodField('get_alterado_em')

    dre = UnidadeLookUpSerializer()

    periodo = PeriodoLookUpSerializer(many=False)

    presentes_na_ata = PresentesAtaDreSerializer(many=True)

    versao = serializers.SerializerMethodField('get_versao')

    motivo_retificacao = serializers.SerializerMethodField('get_motivo_retificacao')

    eh_retificacao = serializers.SerializerMethodField('get_eh_retificacao')

    def get_hora_reuniao(self, obj):
        return obj.hora_reuniao.strftime('%H:%M')

    def get_alterado_em(self, obj):
        return obj.preenchida_em

    def get_versao(self, obj):
        return 'FINAL' if obj.arquivo_pdf else 'PREVIA'

    def get_motivo_retificacao(self, obj):
        if obj.consolidado_dre and obj.consolidado_dre.eh_retificacao:
            return obj.consolidado_dre.motivo_retificacao

        return None

    def get_eh_retificacao(self, obj):
        if obj.consolidado_dre and obj.consolidado_dre.eh_retificacao:
            return True

        return False

    class Meta:
        model = AtaParecerTecnico
        fields = (
            'uuid',
            'arquivo_pdf',
            'status_geracao_pdf',
            'periodo',
            'dre',
            'data_reuniao',
            'numero_ata',
            'local_reuniao',
            'comentarios',
            'hora_reuniao',
            'presentes_na_ata',
            'alterado_em',
            'numero_portaria',
            'data_portaria',
            'versao',
            'motivo_retificacao',
            'eh_retificacao'
        )


class AtaParecerTecnicoCreateSerializer(serializers.ModelSerializer):
    presentes_na_ata = PresentesAtaDreCreateSerializer(many=True, required=False)
    motivo_retificacao = serializers.CharField(source="consolidado_dre__motivo_retificacao", required=False, allow_blank=False)

    dre = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )

    periodo = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Periodo.objects.all()
    )

    def create(self, validated_data):
        presentes_na_ata = validated_data.pop('presentes_na_ata')
        motivo_retificacao = None

        if validated_data.get("consolidado_dre__motivo_retificacao"):
            motivo_retificacao = validated_data.pop('consolidado_dre__motivo_retificacao')

        ata = AtaParecerTecnico.objects.create(**validated_data)

        if motivo_retificacao:
            ata.consolidado_dre.motivo_retificacao = motivo_retificacao
            ata.consolidado_dre.save()

        presentes_lista = []
        for presente in presentes_na_ata:
            presentes_object = PresentesAtaDreCreateSerializer().create(presente)
            presentes_lista.append(presentes_object)

        ata.presentes_na_ata.set(presentes_lista)
        ata.save()
        return ata

    def update(self, instance, validated_data):
        presentes_json = validated_data.pop('presentes_na_ata')
        instance.presentes_na_ata.all().delete()
        presentes_lista = []
        for presente in presentes_json:
            presente_object = PresentesAtaDreCreateSerializer().create(presente)
            presentes_lista.append(presente_object)

        if validated_data.get("consolidado_dre__motivo_retificacao"):
            motivo_retificacao = validated_data.pop('consolidado_dre__motivo_retificacao')
            instance.consolidado_dre.motivo_retificacao = motivo_retificacao
            instance.consolidado_dre.save()

        update_instance_from_dict(instance, validated_data)
        instance.presentes_na_ata.set(presentes_lista)
        instance.save()

        return instance

    class Meta:
        model = AtaParecerTecnico
        exclude = ('id',)
