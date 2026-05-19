from rest_framework import serializers
from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.models.atividade_estatutaria import StatusChoices
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum, TipoAnosAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes
from rest_framework.validators import UniqueTogetherValidator


class AtividadeEstatutariaSerializer(serializers.ModelSerializer):
    ERROR_MSG_JA_CADASTRADO = {"mensagem": "Esta atividade estatutária já existe."}
    MSG_TIPO_NAO_INFORMADO = "Tipo não foi informado."
    MSG_NOME_NAO_INFORMADO = "Atividade Estatutária não foi informada."
    MSG_ANO_NAO_INFORMADO = "Ano não foi informado."
    MSG_MES_NAO_INFORMADO = "Mês não foi informado."
    MSG_STATUS_NAO_INFORMADO = "Status não foi informado."

    nome = serializers.CharField(
        error_messages={
            'null': MSG_NOME_NAO_INFORMADO,
            'blank': MSG_NOME_NAO_INFORMADO,
            'required': MSG_NOME_NAO_INFORMADO,
        },
        required=True
    )

    status = serializers.ChoiceField(
        choices=StatusChoices.choices,
        error_messages={
            'invalid_choice': 'Valor inválido para status de Atividade Estatutária.',
            'blank': MSG_STATUS_NAO_INFORMADO,
            'null': MSG_STATUS_NAO_INFORMADO,
            'required': MSG_STATUS_NAO_INFORMADO,
        },
        required=True
    )

    tipo = serializers.ChoiceField(
        choices=TipoAtividadeEstatutariaEnum.choices(),
        error_messages={
            'invalid_choice': 'Valor inválido para o Tipo da Atividade Estatutária.',
            'blank': MSG_TIPO_NAO_INFORMADO,
            'null': MSG_TIPO_NAO_INFORMADO,
            'required': MSG_TIPO_NAO_INFORMADO,
        },
        required=True
    )

    ano = serializers.ChoiceField(
        choices=TipoAnosAtividadeEstatutariaEnum.choices(),
        error_messages={
            'invalid_choice': 'Valor inválido para o Ano.',
            'null': MSG_ANO_NAO_INFORMADO,
            'blank': MSG_ANO_NAO_INFORMADO,
            'required': MSG_ANO_NAO_INFORMADO,
        },
        required=True
    )

    mes = serializers.ChoiceField(
        choices=Mes.choices,
        error_messages={
            'invalid_choice': 'Valor inválido para o Mês.',
            'null': MSG_MES_NAO_INFORMADO,
            'blank': MSG_MES_NAO_INFORMADO,
            'required': MSG_MES_NAO_INFORMADO,
        },
        required=True
    )

    status_label = serializers.SerializerMethodField()
    tipo_label = serializers.SerializerMethodField()
    ano_label = serializers.SerializerMethodField()
    mes_label = serializers.SerializerMethodField()
    alteracao = serializers.SerializerMethodField()

    def get_alteracao(self, obj):
        alteracoes = self.context.get('alteracoes', {})
        if not alteracoes:
            return None
        secao_key = 'atividades_estatutarias_globais' if obj.paa is None else 'atividades_estatutarias_paa'
        item = alteracoes.get(secao_key, {}).get(str(obj.uuid))
        return item.get('acao') if item else None

    def get_status_label(self, obj):
        return StatusChoices(int(obj.status)).label

    def get_ano_label(self, obj):
        return TipoAnosAtividadeEstatutariaEnum[obj.ano].value if obj.ano else ""

    def get_mes_label(self, obj):
        return Mes(int(obj.mes)).label if obj.mes else ""

    def get_tipo_label(self, obj):
        return TipoAtividadeEstatutariaEnum[obj.tipo].value

    class Meta:
        model = AtividadeEstatutaria
        fields = ('uuid', 'id', 'nome', 'status', 'tipo', 'ano', 'mes',
                  'status_label', 'tipo_label', 'ano_label', 'mes_label', 'paa', 'ordem', 'alteracao')
        read_only_fields = ('uuid', 'id', 'status_label', 'tipo_label', 'ano_label', 'mes_label', 'paa', 'alteracao')
        validators = [
            UniqueTogetherValidator(
                queryset=AtividadeEstatutaria.objects.all(),
                fields=['nome', 'mes', 'tipo'],
                message="Esta atividade estatutária já existe."
            )
        ]
