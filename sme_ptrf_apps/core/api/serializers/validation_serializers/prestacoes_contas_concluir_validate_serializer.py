import logging

from rest_framework import serializers
from sme_ptrf_apps.core.models import Associacao, Periodo, PrestacaoConta
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices

logger = logging.getLogger(__name__)

STATUS_PRESIDENTE_CHOICES = (
    ('PRESENTE', 'Presente'),
    ('AUSENTE', 'Ausente'),
)

# Oito cargos da diretoria executiva, sem o próprio presidente (índice 0).
CARGOS_SUBSTITUTO_PRESIDENTE = CargoComposicaoVacanciaChoices.choices[1:9]
CARGOS_CONSELHEIRO_ASSINATURA = CargoComposicaoVacanciaChoices.choices[9:]


class PrestacoesContasConcluirValidateSerializer(serializers.Serializer):  # noqa
    associacao_uuid = serializers.UUIDField(required=True, allow_null=False)
    periodo_uuid = serializers.UUIDField(required=True, allow_null=False)
    justificativa_acertos_pendentes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    status_presidente = serializers.ChoiceField(
        choices=STATUS_PRESIDENTE_CHOICES,
        required=False,
        allow_null=True,
    )
    cargo_substituto_presidente_ausente = serializers.ChoiceField(
        choices=CARGOS_SUBSTITUTO_PRESIDENTE,
        required=False,
        allow_null=True,
    )
    cargo_conselheiro_assinatura = serializers.ChoiceField(
        choices=CARGOS_CONSELHEIRO_ASSINATURA,
        required=False,
        allow_null=True,
    )

    def validate_associacao_uuid(self, value):  # noqa
        try:
            Associacao.by_uuid(value)
        except Associacao.DoesNotExist:  # noqa
            logger.error(f'Associação com uuid {value} não encontrada.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Associação {value}.")

        return value

    def validate_periodo_uuid(self, value):  # noqa
        try:
            Periodo.by_uuid(value)
        except Periodo.DoesNotExist:  # noqa
            logger.error(f'Período com uuid {value} não encontrado.')
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o uuid de Período {value}.")

        return value

    def validate(self, attrs: dict) -> dict:
        """Valida a conclusão da prestação e o substituto do presidente ausente.

        Com status PRESENTE, descarta o cargo substituto. Com AUSENTE, exige o cargo.

        Args:
            attrs: dados já validados campo a campo.

        Returns:
            Os mesmos dados, com associação, período e prestação resolvidos.

        Raises:
            serializers.ValidationError: se a prestação não puder ser concluída ou
                o substituto do presidente ausente não for informado.
        """
        from sme_ptrf_apps.core.services.periodo_services import (
            pc_tem_solicitacoes_de_acerto_pendentes,
        )

        status_presidente = attrs.get('status_presidente')
        cargo_substituto = attrs.get('cargo_substituto_presidente_ausente')
        if status_presidente == 'PRESENTE':
            attrs['cargo_substituto_presidente_ausente'] = None
        elif status_presidente == 'AUSENTE' and not cargo_substituto:
            raise serializers.ValidationError(
                'É necessário informar o cargo substituto quando o presidente está ausente.'
            )

        associacao = Associacao.by_uuid(attrs['associacao_uuid'])
        periodo = Periodo.by_uuid(attrs['periodo_uuid'])

        prestacao_conta = PrestacaoConta.objects.filter(
            associacao=associacao,
            periodo=periodo
        ).first()

        if prestacao_conta:
            pc_nao_pode_ser_concluida = prestacao_conta.status not in (
                PrestacaoConta.STATUS_NAO_APRESENTADA,
                PrestacaoConta.STATUS_DEVOLVIDA
            )
            if pc_nao_pode_ser_concluida:
                raise serializers.ValidationError(
                    "A Prestação de Contas só pode ser concluída se estiver com status 'Não Apresentada' ou 'Devolvida'."
                )

            if pc_tem_solicitacoes_de_acerto_pendentes(prestacao_conta):
                raise serializers.ValidationError(
                    "A Prestação de Contas possui solicitações de acerto pendentes e não pode ser concluída."
                )

            contas_alteradas = prestacao_conta.contas_saldos_alterados_sem_solicitacao()

            if contas_alteradas:
                nomes = [c.tipo_conta.nome for c in contas_alteradas]

                if len(nomes) == 1:
                    mensagem = (
                        f"O saldo bancário da conta {nomes[0]} foi modificado e não é permitido devolução. "
                        "Favor retornar o saldo bancário para o valor original indicado na entrega da prestação de contas."
                    )
                else:
                    mensagem = (
                        f"O saldo bancário das contas {', '.join(nomes)} foi modificado e não é permitido devolução. "
                        "Favor retornar os saldos bancários para os valores originais indicados na entrega da prestação de contas."
                    )

                raise serializers.ValidationError({
                    'erro': 'prestacao_com_saldos_alterados_sem_solicitacao',
                    'mensagem': mensagem
                })

        attrs['associacao'] = associacao
        attrs['periodo'] = periodo
        attrs['prestacao_conta'] = prestacao_conta
        return attrs
