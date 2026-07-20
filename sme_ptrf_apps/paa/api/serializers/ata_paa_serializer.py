"""Serializers para o gerenciamento de atas do Plano Anual de Atividades."""

import logging

from django.db import transaction
from rest_framework import serializers
from sme_ptrf_apps.mandatos.services.composicao_service import ServicoRecuperaComposicaoPorData

from sme_ptrf_apps.core.api.serializers import AssociacaoInfoAtaSerializer
from sme_ptrf_apps.paa.api.serializers.presentes_ata_paa_serializer import (PresentesAtaPaaSerializer,
                                                                            PresentesAtaPaaCreateSerializer)
from sme_ptrf_apps.paa.models import AtaPaa, Paa
from sme_ptrf_apps.paa.services.validacao_edicao_ata_paa_service import validar_edicao_ata_paa
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


class AtaPaaLookUpSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem e identificação de atas do PAA."""

    nome = serializers.SerializerMethodField('get_nome_ata')
    alterado_em = serializers.SerializerMethodField('get_alterado_em')
    completa = serializers.SerializerMethodField('get_completa')

    def get_nome_ata(self, obj: AtaPaa) -> str:
        """Retorna o nome da ata.

        Returns:
            str: Nome da ata.
        """
        return obj.nome

    def get_alterado_em(self, obj: AtaPaa) -> str:
        """Retorna a data em que a ata foi preenchida ou alterada.

        Args:
            obj: Instância da ata do PAA.

        Returns:
            str: Data de alteração/preenchimento da ata.
        """
        return obj.preenchida_em

    def get_completa(self, obj: AtaPaa) -> bool:
        """Indica se a ata está completa.

        Args:
            obj: Instância da ata do PAA.

        Returns:
            bool: Valor que representa se a ata está completa.
        """
        return obj.completa

    class Meta:
        model = AtaPaa
        fields = ('uuid', 'nome', 'alterado_em', 'completa')


class AtaPaaSerializer(serializers.ModelSerializer):
    """Serializer principal para representação detalhada de uma ata do PAA."""

    nome = serializers.SerializerMethodField('get_nome_ata')
    hora_reuniao = serializers.SerializerMethodField('get_hora_reuniao')
    associacao = serializers.SerializerMethodField('get_associacao')
    completa = serializers.SerializerMethodField('get_completa')
    precisa_professor_gremio = serializers.SerializerMethodField('get_precisa_professor_gremio')
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Paa.objects.all()
    )

    presentes_na_ata_paa = PresentesAtaPaaSerializer(many=True)

    def get_nome_ata(self, obj: AtaPaa) -> str:
        """Retorna o nome da ata.

        Returns:
            str: Nome da ata.
        """
        return obj.nome

    def get_hora_reuniao(self, obj: AtaPaa) -> str:
        """Normaliza o valor da hora da reunião para o formato HH:MM.

        Args:
            obj: Instância da ata do PAA.

        Returns:
            str: Hora formatada no padrão HH:MM.
        """
        if obj.hora_reuniao:
            if isinstance(obj.hora_reuniao, str):
                return obj.hora_reuniao[:5] if len(obj.hora_reuniao) >= 5 else obj.hora_reuniao
            return obj.hora_reuniao.strftime('%H:%M')
        return "00:00"

    def get_associacao(self, obj: AtaPaa) -> dict | None:
        """Retorna os dados resumidos da associação vinculada ao PAA.

        Args:
            obj: Instância da ata do PAA.

        Returns:
            dict | None: Dados da associação em formato serializado ou None.
        """
        if obj.paa and obj.paa.associacao:
            return AssociacaoInfoAtaSerializer(obj.paa.associacao).data
        return None

    def get_completa(self, obj: AtaPaa) -> bool:
        """Informa se a ata está completa.

        Returns:
            bool: Indicador de completude da ata.
        """
        return obj.completa

    def get_precisa_professor_gremio(self, obj: AtaPaa) -> bool:
        """Indica se a unidade precisa de professor de grêmio para a ata.

        Args:
            obj: Instância da ata do PAA.

        Returns:
            bool: Valor que indica se é necessário professor de grêmio.
        """
        return obj.precisa_professor_gremio

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
            'presidente_reuniao',
            'cargo_presidente_reuniao',
            'secretario_reuniao',
            'cargo_secretaria_reuniao',
            'comentarios',
            'parecer_conselho',
            'presentes_na_ata_paa',
            'hora_reuniao',
            'justificativa',
            'justificativa_retificacao',
            'composicao',
            'completa',
            'precisa_professor_gremio',
            'alterado_em',
        )


class AtaPaaCreateSerializer(serializers.ModelSerializer):
    """Serializer responsável por criar e atualizar atas do PAA, incluindo presentes."""

    nome = serializers.SerializerMethodField('get_nome_ata')
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Paa.objects.all()
    )

    presentes_na_ata_paa = PresentesAtaPaaCreateSerializer(many=True, required=False)

    def get_nome_ata(self, obj: AtaPaa) -> str:
        """Retorna o nome da ata.

        Returns:
            str: Nome da ata.
        """
        return obj.nome

    def _checar_permite_edicao_ata(self, ata_paa: AtaPaa) -> None:
        """Valida se a ata pode ser editada antes de atualizar seus dados.

        Args:
            ata_paa: Instância da ata do PAA a ser validada.

        Returns:
            None: Nenhum valor é retornado, mas pode levantar ValidationError.
        """
        validacao = validar_edicao_ata_paa(ata_paa)
        if not validacao.get('is_valid'):
            raise serializers.ValidationError({'mensagem': validacao.get('mensagem')})

    def create(self, validated_data: dict) -> AtaPaa:
        """Cria uma nova ata do PAA e persiste os presentes associados.

        Args:
            validated_data: Dados validados para criação da ata.

        Returns:
            AtaPaa: Instância criada da ata do PAA.
        """
        with transaction.atomic():
            presentes_na_ata_paa = validated_data.pop('presentes_na_ata_paa', [])
            ata_paa = AtaPaa.objects.create(**validated_data)

            presentes_lista = []
            presidente_participante = None
            secretario_participante = None

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
                    presidente = presente.get('presidente_da_reuniao', False)
                    secretario = presente.get('secretario_da_reuniao', False)

                    presente_sem_cargos = presente.copy()
                    presente_sem_cargos.pop('presidente_da_reuniao', None)
                    presente_sem_cargos.pop('secretario_da_reuniao', None)

                    presente_sem_cargos['ata_paa'] = ata_paa.uuid
                    presente_serializer = PresentesAtaPaaCreateSerializer(data=presente_sem_cargos)
                    presente_serializer.is_valid(raise_exception=True)
                    presente_object = presente_serializer.save()

                    if presidente:
                        presidente_participante = presente_object
                    elif secretario:
                        secretario_participante = presente_object

                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)
            else:
                for presente in presentes_na_ata_paa:
                    presidente = presente.get('presidente_da_reuniao', False)
                    secretario = presente.get('secretario_da_reuniao', False)

                    presente_sem_cargos = presente.copy()
                    presente_sem_cargos.pop('presidente_da_reuniao', None)
                    presente_sem_cargos.pop('secretario_da_reuniao', None)

                    presente_sem_cargos['ata_paa'] = ata_paa.uuid
                    presente_serializer = PresentesAtaPaaCreateSerializer(data=presente_sem_cargos)
                    presente_serializer.is_valid(raise_exception=True)
                    presente_object = presente_serializer.save()

                    if presidente:
                        presidente_participante = presente_object
                    elif secretario:
                        secretario_participante = presente_object

                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)

            ata_paa.presentes_na_ata_paa.set(presentes_lista)

            if presidente_participante:
                ata_paa.presidente_da_reuniao = presidente_participante
            if secretario_participante:
                ata_paa.secretario_da_reuniao = secretario_participante

            ata_paa.arquivo_pdf = None
            ata_paa.arquivo_pdf_nao_gerado()
            ata_paa.save()

            return ata_paa

    def update(self, instance: AtaPaa, validated_data: dict) -> AtaPaa:
        """Atualiza a ata do PAA e recalcula os presentes e cargos da reunião.

        Args:
            instance: Instância atual da ata do PAA.
            validated_data: Dados validados para atualização da ata.

        Returns:
            AtaPaa: Instância atualizada da ata do PAA.
        """
        self._checar_permite_edicao_ata(instance)

        with transaction.atomic():
            presentes_json = validated_data.pop('presentes_na_ata_paa', [])

            if instance.presidente_da_reuniao:
                instance.presidente_da_reuniao = None
            if instance.secretario_da_reuniao:
                instance.secretario_da_reuniao = None
            instance.save()

            instance.presentes_na_ata_paa.all().delete()
            presentes_lista = []
            presidente_participante = None
            secretario_participante = None

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
                    presidente = presente.get('presidente_da_reuniao', False)
                    secretario = presente.get('secretario_da_reuniao', False)

                    presente_sem_cargos = presente.copy()
                    presente_sem_cargos.pop('presidente_da_reuniao', None)
                    presente_sem_cargos.pop('secretario_da_reuniao', None)

                    presente_sem_cargos['ata_paa'] = instance.uuid
                    presente_serializer = PresentesAtaPaaCreateSerializer(data=presente_sem_cargos)
                    presente_serializer.is_valid(raise_exception=True)
                    presente_object = presente_serializer.save()

                    if presidente:
                        presidente_participante = presente_object
                    elif secretario:
                        secretario_participante = presente_object

                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)

            else:
                for presente in presentes_json:
                    presidente = presente.get('presidente_da_reuniao', False)
                    secretario = presente.get('secretario_da_reuniao', False)

                    presente_sem_cargos = presente.copy()
                    presente_sem_cargos.pop('presidente_da_reuniao', None)
                    presente_sem_cargos.pop('secretario_da_reuniao', None)

                    presente_sem_cargos['ata_paa'] = instance.uuid
                    presente_serializer = PresentesAtaPaaCreateSerializer(data=presente_sem_cargos)
                    presente_serializer.is_valid(raise_exception=True)
                    presente_object = presente_serializer.save()

                    if presidente or validated_data['presidente_reuniao'] == presente['nome']:
                        presidente_participante = presente_object
                    elif secretario or validated_data['secretario_reuniao'] == presente['nome']:
                        secretario_participante = presente_object

                    presente_object.eh_conselho_fiscal()
                    presentes_lista.append(presente_object)

            update_instance_from_dict(instance, validated_data)
            instance.presentes_na_ata_paa.set(presentes_lista)

            # Define presidente e secretário após criar todos os presentes
            if presidente_participante:
                instance.presidente_da_reuniao = presidente_participante
            if secretario_participante:
                instance.secretario_da_reuniao = secretario_participante

            instance.arquivo_pdf = None
            instance.arquivo_pdf_nao_gerado()
            instance.save()

            return instance

    class Meta:
        model = AtaPaa
        exclude = ('id',)
