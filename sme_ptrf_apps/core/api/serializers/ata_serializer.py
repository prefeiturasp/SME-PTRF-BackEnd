import logging

from rest_framework import serializers
from sme_ptrf_apps.mandatos.services.composicao_service import ServicoRecuperaComposicaoPorData

from ...api.serializers import AssociacaoInfoAtaSerializer
from ...api.serializers.periodo_serializer import PeriodoLookUpSerializer
from ...api.serializers.presentes_ata_serializer import PresentesAtaSerializer, PresentesAtaCreateSerializer
from ...models import Ata, PrestacaoConta
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)

class AtaLookUpSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    alterado_em = serializers.SerializerMethodField('get_alterado_em')

    def get_nome_ata(self, obj):
        return obj.nome

    def get_alterado_em(self, obj):
        return obj.preenchida_em

    class Meta:
        model = Ata
        fields = ('uuid', 'nome', 'alterado_em', "completa")


class AtaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    hora_reuniao = serializers.SerializerMethodField('get_hora_reuniao')
    associacao = AssociacaoInfoAtaSerializer(many=False)
    periodo = PeriodoLookUpSerializer(many=False)
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )
    completa = serializers.SerializerMethodField('get_completa')

    presentes_na_ata = PresentesAtaSerializer(many=True)

    def get_nome_ata(self, obj):
        return obj.nome

    def get_hora_reuniao(self, obj):
        return obj.hora_reuniao.strftime('%H:%M')
    
    def get_completa(self, obj):
        if obj.completa:
            return True
        return False

    class Meta:
        model = Ata
        fields = (
            'uuid',
            'arquivo_pdf',
            'status_geracao_pdf',
            'prestacao_conta',
            'nome',
            'periodo',
            'associacao',
            'tipo_ata',
            'tipo_reuniao',
            'convocacao',
            'data_reuniao',
            'local_reuniao',
            'presidente_reuniao',
            'cargo_presidente_reuniao',
            'secretario_reuniao',
            'cargo_secretaria_reuniao',
            'comentarios',
            'parecer_conselho',
            'retificacoes',
            'presentes_na_ata',
            'hora_reuniao',
            'justificativa_repasses_pendentes',
            'completa',
        )


class AtaCreateSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField('get_nome_ata')
    associacao = AssociacaoInfoAtaSerializer(many=False)
    periodo = PeriodoLookUpSerializer(many=False)
    prestacao_conta = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrestacaoConta.objects.all()
    )

    presentes_na_ata = PresentesAtaCreateSerializer(many=True, required=False)

    def get_nome_ata(self, obj):
        return obj.nome

    def create(self, validated_data):
        presentes_na_ata = validated_data.pop('presentes_na_ata')
        ata = Ata.objects.create(**validated_data)

        presentes_lista = []
        
        flags = get_waffle_flag_model()
        if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
            if validated_data and validated_data["data_reuniao"]:
                servico_composicao = ServicoRecuperaComposicaoPorData()
                composicao = servico_composicao.get_composicao_por_data_e_associacao(validated_data["data_reuniao"], ata.associacao)
                ata.composicao = composicao
            else:
                ata.composicao = None
            
            for presente in presentes_na_ata:
                presidente = presente.pop('presidente_da_reuniao', False)
                secretario = presente.pop('secretario_da_reuniao', False)
                
                presente_object = PresentesAtaCreateSerializer().create(presente)
                presente_object.save()
                
                if presidente:
                    ata.presidente_da_reuniao = presentes_object
                    
                elif secretario:
                    ata.secretario_da_reuniao = presentes_object

                presentes_object.eh_conselho_fiscal()
                presentes_lista.append(presentes_object)
        else:
            for presente in presentes_na_ata:
                presentes_object = PresentesAtaCreateSerializer().create(presente)
                presentes_object.eh_conselho_fiscal()
                presentes_lista.append(presentes_object)

        ata.presentes_na_ata.set(presentes_lista)
        ata.arquivo_pdf = None
        ata.arquivo_pdf_nao_gerado()
        ata.save()

        return ata

    def update(self, instance, validated_data):
        presentes_json = validated_data.pop('presentes_na_ata')
        
        if instance.presidente_da_reuniao:
            instance.presidente_da_reuniao = None
        if instance.secretario_da_reuniao:
            instance.secretario_da_reuniao = None
        instance.save()

        instance.presentes_na_ata.all().delete()
        presentes_lista = []
        
        flags = get_waffle_flag_model()
        if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
            if validated_data and validated_data["data_reuniao"]:
                servico_composicao = ServicoRecuperaComposicaoPorData()
                composicao = servico_composicao.get_composicao_por_data_e_associacao(validated_data["data_reuniao"], instance.associacao)
                instance.composicao = composicao
            else:
                instance.composicao = None

            for presente in presentes_json:
                presidente = presente.pop('presidente_da_reuniao', False)
                secretario = presente.pop('secretario_da_reuniao', False)
                
                presente_object = PresentesAtaCreateSerializer().create(presente)
                presente_object.save()
                
                if presidente:
                    instance.presidente_da_reuniao = presente_object
                    
                elif secretario:
                    instance.secretario_da_reuniao = presente_object
                    
                presente_object.eh_conselho_fiscal()
                presentes_lista.append(presente_object)
            
        else:
            for presente in presentes_json:
                presente_object = PresentesAtaCreateSerializer().create(presente)
                presente_object.eh_conselho_fiscal()
                presentes_lista.append(presente_object)

        update_instance_from_dict(instance, validated_data)
        instance.presentes_na_ata.set(presentes_lista)
        instance.arquivo_pdf = None
        instance.arquivo_pdf_nao_gerado()
        instance.save()

        return instance

    class Meta:
        model = Ata
        exclude = ('id',)
