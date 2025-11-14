import logging

from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.mandatos.services.composicao_service import ServicoRecuperaComposicaoPorData

from sme_ptrf_apps.core.api.serializers import AssociacaoInfoAtaSerializer
from sme_ptrf_apps.paa.api.serializers.periodo_paa_serializer import PeriodoPaaSerializer
from sme_ptrf_apps.paa.api.serializers.presentes_ata_paa_serializer import PresentesAtaPaaSerializer, PresentesAtaPaaCreateSerializer
from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


class AtaPaaLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    alterado_em = serializers.SerializerMethodField('get_alterado_em')

    def get_nome_ata(self, obj):
        return obj.nome

    def get_alterado_em(self, obj):
        return obj.preenchida_em

    class Meta:
        model = AtaPaa
        fields = ('uuid', 'nome', 'alterado_em')


class AtaPaaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    hora_reuniao = serializers.SerializerMethodField('get_hora_reuniao')
    associacao = serializers.SerializerMethodField('get_associacao')
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Paa.objects.all()
    )

    presentes_na_ata_paa = PresentesAtaPaaSerializer(many=True)

    def get_nome_ata(self, obj):
        return obj.nome

    def get_hora_reuniao(self, obj):
        if obj.hora_reuniao:
            if isinstance(obj.hora_reuniao, str):
                return obj.hora_reuniao[:5] if len(obj.hora_reuniao) >= 5 else obj.hora_reuniao
            return obj.hora_reuniao.strftime('%H:%M')
        return "00:00"
    
    def get_associacao(self, obj):
        if obj.paa and obj.paa.associacao:
            return AssociacaoInfoAtaSerializer(obj.paa.associacao).data
        return None

    class Meta:
        model = AtaPaa
        fields = (
            'uuid',
            'arquivo_pdf',
            'status_geracao_pdf',
            'paa',
            'nome',
            'associacao',
            'tipo_ata',
            'tipo_reuniao',
            'convocacao',
            'data_reuniao',
            'local_reuniao',
            'comentarios',
            'parecer_conselho',
            'presentes_na_ata_paa',
            'hora_reuniao',
            'justificativa',
            'composicao',
        )


class AtaPaaCreateSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Paa.objects.all()
    )

    presentes_na_ata_paa = PresentesAtaPaaCreateSerializer(many=True, required=False)

    def get_nome_ata(self, obj):
        return obj.nome

    def create(self, validated_data):
        with transaction.atomic():
            presentes_na_ata_paa = validated_data.pop('presentes_na_ata_paa', [])
            ata_paa = AtaPaa.objects.create(**validated_data)

            presentes_lista = []
            
            flags = get_waffle_flag_model()
            if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
                if validated_data and validated_data.get("data_reuniao"):
                    servico_composicao = ServicoRecuperaComposicaoPorData()
                    composicao = servico_composicao.get_composicao_por_data_e_associacao(
                        validated_data["data_reuniao"], 
                        ata_paa.paa.associacao
                    )
                    ata_paa.composicao = composicao
                else:
                    ata_paa.composicao = None
                
                for presente in presentes_na_ata_paa:
                    presidente = presente.pop('presidente_da_reuniao', False)
                    secretario = presente.pop('secretario_da_reuniao', False)
                    professor_gremio = presente.get('professor_gremio', False)
                    
                    # Validação: professor do grêmio não pode ser presidente nem secretário
                    if professor_gremio and (presidente or secretario):
                        raise serializers.ValidationError({
                            'presentes_na_ata_paa': 'O professor do grêmio não pode ser presidente nem secretário da reunião.'
                        })
                    
                    presente_object = PresentesAtaPaaCreateSerializer().create(presente)
                    presente_object.ata_paa = ata_paa
                    presente_object.save()
                    
                    if presidente:
                        ata_paa.presidente_da_reuniao = presente_object
                        
                    elif secretario:
                        ata_paa.secretario_da_reuniao = presente_object

                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)
            else:
                for presente in presentes_na_ata_paa:
                    presente_object = PresentesAtaPaaCreateSerializer().create(presente)
                    presente_object.ata_paa = ata_paa
                    presente_object.save()
                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)

            ata_paa.presentes_na_ata_paa.set(presentes_lista)
            ata_paa.arquivo_pdf = None
            ata_paa.arquivo_pdf_nao_gerado()
            ata_paa.save()

            return ata_paa

    def update(self, instance, validated_data):
        with transaction.atomic():
            presentes_json = validated_data.pop('presentes_na_ata_paa', [])
            
            if instance.presidente_da_reuniao:
                instance.presidente_da_reuniao = None
            if instance.secretario_da_reuniao:
                instance.secretario_da_reuniao = None
            instance.save()

            instance.presentes_na_ata_paa.all().delete()
            presentes_lista = []
            
            flags = get_waffle_flag_model()
            if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
                if validated_data and validated_data.get("data_reuniao"):
                    servico_composicao = ServicoRecuperaComposicaoPorData()
                    composicao = servico_composicao.get_composicao_por_data_e_associacao(
                        validated_data["data_reuniao"], 
                        instance.paa.associacao
                    )
                    instance.composicao = composicao
                else:
                    instance.composicao = None

                for presente in presentes_json:
                    presidente = presente.pop('presidente_da_reuniao', False)
                    secretario = presente.pop('secretario_da_reuniao', False)
                    professor_gremio = presente.get('professor_gremio', False)
                    
                    # Validação: professor do grêmio não pode ser presidente nem secretário
                    if professor_gremio and (presidente or secretario):
                        raise serializers.ValidationError({
                            'presentes_na_ata_paa': 'O professor do grêmio não pode ser presidente nem secretário da reunião.'
                        })
                    
                    presente_object = PresentesAtaPaaCreateSerializer().create(presente)
                    presente_object.ata_paa = instance
                    presente_object.save()
                    
                    if presidente:
                        instance.presidente_da_reuniao = presente_object
                        
                    elif secretario:
                        instance.secretario_da_reuniao = presente_object
                        
                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)
                
            else:
                for presente in presentes_json:
                    presente_object = PresentesAtaPaaCreateSerializer().create(presente)
                    presente_object.ata_paa = instance
                    presente_object.save()
                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)

            update_instance_from_dict(instance, validated_data)
            instance.presentes_na_ata_paa.set(presentes_lista)
            instance.arquivo_pdf = None
            instance.arquivo_pdf_nao_gerado()
            instance.save()

            return instance

    class Meta:
        model = AtaPaa
        exclude = ('id',)

