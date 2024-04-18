from waffle import flag_is_active

from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoLookupSerializer, PeriodoLookUpSerializer
from sme_ptrf_apps.core.models import ProcessoAssociacao, Associacao, Periodo


class ProcessoAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )
    periodos = serializers.SlugRelatedField(
        many=True,
        slug_field='uuid',
        queryset=Periodo.objects.all(),
        required=False
    )

    def validate(self, data):
        request = self.context.get('request')

        flag_ativa = flag_is_active(request, 'periodos-processo-sei')

        if not flag_ativa and 'periodos' in data:
            raise serializers.ValidationError({
                "periodos": "A feature flag 'periodos-processo-sei' está desligada. Não é possível fornecer 'periodos'."
            })

        if flag_ativa:
            periodos = data.get('periodos', [])
            if not periodos:
                raise serializers.ValidationError({
                    "periodos": "É necessário informar ao menos um período quando a feature 'periodos-processo-sei' está ativa."
                })

            ano_processo = data.get('ano')
            if periodos and ano_processo:
                for periodo in periodos:
                    ano_periodo = periodo.referencia.split('.')[0]
                    if ano_periodo != ano_processo:
                        raise serializers.ValidationError({
                            "periodos": f"Todos os períodos devem estar no mesmo ano do campo 'ano' ({ano_processo})."
                        })

            associacao = data.get('associacao')
            periodos = data.get('periodos', [])
            numero_processo = data.get('numero_processo')
            
            # Verifica se já existe na associação no mesmo ano o mesmo numero
            if numero_processo and associacao and ano_processo:
                processos_existentes = ProcessoAssociacao.objects.filter(
                    associacao=associacao, numero_processo=numero_processo, ano=ano_processo
                )

                if self.instance:
                    processos_existentes = processos_existentes.exclude(pk=self.instance.pk)

                if processos_existentes.exists():
                    raise serializers.ValidationError({
                        "numero_processo": f"Este número de processo SEI já existe para o ano informado."
                    })

            # Verifica se os períodos estão sendo reutilizados na mesma associação
            for periodo in periodos:
                processos_existentes = ProcessoAssociacao.objects.filter(
                    associacao=associacao, periodos=periodo
                )

                # Se estamos atualizando, excluímos o objeto atual da verificação para evitar falso-positivo
                if self.instance:
                    processos_existentes = processos_existentes.exclude(pk=self.instance.pk)

                if processos_existentes.exists():
                    raise serializers.ValidationError({
                        "periodos": f"O período {periodo.referencia} já está associado a outro ProcessoAssociacao para a associação {associacao}."
                    })

        return data

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano', 'periodos')

    def create(self, validated_data):
        periodos_data = validated_data.pop('periodos', [])
        processo_associacao = ProcessoAssociacao.objects.create(**validated_data)
        processo_associacao.periodos.set(periodos_data)
        return processo_associacao

    def update(self, instance, validated_data):
        periodos_data = validated_data.pop('periodos', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if periodos_data is not None:
            instance.periodos.set(periodos_data)
        return instance


class ProcessoAssociacaoRetrieveSerializer(serializers.ModelSerializer):

    associacao = AssociacaoLookupSerializer()
    permite_exclusao = serializers.SerializerMethodField('get_permite_exclusao')
    tooltip_exclusao = serializers.SerializerMethodField('get_tooltip_exclusao')
    periodos = PeriodoLookUpSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessoAssociacao
        fields = ('uuid', 'associacao', 'numero_processo', 'ano', 'criado_em', 'alterado_em',
                  'permite_exclusao', 'tooltip_exclusao', 'periodos',)

    def get_tooltip_exclusao(self, obj):
        request = self.context.get('request', None)

        msg = "Não é possível excluir o número desse processo SEI, pois este já está vinculado a uma prestação de contas. Caso necessário, é possível editá-lo."

        if flag_is_active(request, 'periodos-processo-sei'):
            return msg if obj.prestacoes_vinculadas_aos_periodos.exists() else ""
        else:
            return msg if obj.e_o_ultimo_processo_do_ano_com_pcs_vinculada else ""

    def get_permite_exclusao(self, obj):
        request = self.context.get('request', None)

        if flag_is_active(request, 'periodos-processo-sei'):
            return not obj.prestacoes_vinculadas_aos_periodos.exists()
        else:
            return not obj.e_o_ultimo_processo_do_ano_com_pcs_vinculada
