
from datetime import date

from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Trim

from sme_ptrf_apps.core.models import Ata, Participante
from waffle import get_waffle_flag_model
from sme_ptrf_apps.mandatos.choices import (
    CargoComposicaoVacanciaChoices as Cargos,
)
from sme_ptrf_apps.mandatos.models import (
    CargoComposicaoVacancia,
    ComposicaoVacancia,
    OcupanteCargo,
)


class ServicoAtualizacaoMembrosAtas:
    """Sincroniza os membros das atas com o histórico de cargos."""

    flags = get_waffle_flag_model()

    @classmethod
    @transaction.atomic
    def atualizar_atas_por_periodo(
        cls,
        composicao_vacancia: ComposicaoVacancia,
        cargo_associacao: str,
        data_inicio: date,
        data_fim: date,
    ) -> None:

        if data_inicio > data_fim:
            return

        historico_v2 = cls.flags.objects.filter(
            name="historico-de-membros-v2",
            everyone=True,
        ).exists()

        if not historico_v2:
            return

        atas = Ata.objects.filter(
            associacao=composicao_vacancia.associacao,
            tipo_ata__in=[
                Ata.ATA_APRESENTACAO,
                Ata.ATA_RETIFICACAO,
            ],
            status_geracao_pdf=Ata.STATUS_NAO_GERADO,
            data_reuniao__isnull=False,
            data_reuniao__range=(data_inicio, data_fim),
        ).order_by("data_reuniao", "pk")


        historico_v1 = cls.flags.objects.filter(
            name="historico-de-membros",
            everyone=True,
        ).exists()

        for ata in atas:
            # Ata sem membros ainda será preenchida pelo front a partir da composição
            if not ata.presentes_na_ata.filter(membro=True).exists():
                continue

            registro = CargoComposicaoVacancia.objects.filter(
                composicao=composicao_vacancia,
                cargo_associacao=cargo_associacao,
                data_inicio_no_cargo__lte=ata.data_reuniao,
                data_fim_no_cargo__gte=ata.data_reuniao,
            ).select_related('ocupante_do_cargo').first()

            if not registro:
                continue

            participante = cls._sincronizar_participante(
                ata=ata,
                cargo_associacao=cargo_associacao,
                registro=registro,
                historico_ativo=(historico_v1 or historico_v2)
            )

            if registro.ocupante_do_cargo:
                cls._remove_ocupante_como_nao_membro(ata, participante, registro.ocupante_do_cargo)
     
    @staticmethod
    def _dados_participante(registro: CargoComposicaoVacancia) -> dict:
        ocupante = registro.ocupante_do_cargo

        if ocupante is None:
            return {
                'identificacao': '',
                'nome': '',
                'vago': True,
                'presente': False,
                'data_inicio_no_cargo': registro.data_inicio_no_cargo,
            }

        return {
            'identificacao': ocupante.codigo_identificacao or ocupante.cpf_responsavel or '',
            'nome': ocupante.nome,
            'vago': False,
            'presente': True,
            'data_inicio_no_cargo': registro.data_inicio_no_cargo,
        }

    @staticmethod
    def _limpar_referencias_ata(ata: Ata, membros, flag_historico: bool):
        if not membros:
            return

        ids_membros = {membro.pk for membro in membros}
        campos_atualizados = set()         

        # Identifica atas que possuem informações legadas,
        # mesmo quando a flag de histórico estiver ativada.
        tem_campos_legados = any([
            ata.presidente_reuniao,
            ata.cargo_presidente_reuniao,
            ata.secretario_reuniao,
            ata.cargo_secretaria_reuniao,
        ])

        # Considera o fallback utilizado em Ata.completa.
        usa_campos_legados = (
            not flag_historico
            or tem_campos_legados
            or not (
                ata.presidente_da_reuniao_id
                and ata.secretario_da_reuniao_id
            )
        )

        # Histórico v1/v2: limpa as FKs, caso apontem
        # para algum dos participantes afetados.
        if flag_historico:
            if ata.presidente_da_reuniao_id in ids_membros:
                ata.presidente_da_reuniao = None
                campos_atualizados.add("presidente_da_reuniao")

            if ata.secretario_da_reuniao_id in ids_membros:
                ata.secretario_da_reuniao = None
                campos_atualizados.add("secretario_da_reuniao")

        # Legado: limpa os campos textuais correspondentes
        if usa_campos_legados:
            ata_presidente_reuniao = (ata.presidente_reuniao or "").lower()
            ata_secretario_reuniao = (ata.secretario_reuniao or "").lower()

            ata_cargo_presidente = (ata.cargo_presidente_reuniao or "").lower()
            ata_cargo_secretaria = (ata.cargo_secretaria_reuniao or "").lower()
            
            for membro in membros:
                membro_cargo = (membro.cargo or "").lower()
                membro_nome = (membro.nome or "").lower()

                if (
                    ata_presidente_reuniao == membro_nome
                    and ata_cargo_presidente == membro_cargo
                ):
                    ata.presidente_reuniao = ""
                    ata.cargo_presidente_reuniao = ""

                    campos_atualizados.update([
                        "presidente_reuniao",
                        "cargo_presidente_reuniao",
                    ])
                
                if (
                    ata_secretario_reuniao == membro_nome
                    and ata_cargo_secretaria == membro_cargo
                ):
                    ata.secretario_reuniao = ""
                    ata.cargo_secretaria_reuniao = ""

                    campos_atualizados.update([
                        "secretario_reuniao",
                        "cargo_secretaria_reuniao",
                    ])

        if campos_atualizados:
            ata.save(update_fields=list(campos_atualizados))

    
    @staticmethod
    def _remove_ocupante_como_nao_membro(
        ata: Ata,
        participante: Participante,
        ocupante: OcupanteCargo,
    ) -> None:
        """Remove o ocupante da lista de não membros da ata, mantendo-o apenas no cargo.

        Se o registro removido era o presidente ou secretário da reunião, o vínculo é
        transferido para o participante do cargo.

        O nome é comparado sem diferenciar maiúsculas/minúsculas e ignorando espaços nas
        pontas, já que nas atas ele pode vir da API do servidor (caixa alta) ou digitado.
        """
        identificacoes = [i for i in (ocupante.codigo_identificacao, ocupante.cpf_responsavel) if i]
        nome_ocupante = (ocupante.nome or '').strip()

        criterios = Q()
        if identificacoes:
            criterios |= Q(identificacao__in=identificacoes)
        if nome_ocupante:
            criterios |= Q(nome_sem_espacos__iexact=nome_ocupante)

        if not criterios:
            return

        nao_membros = (
            ata.presentes_na_ata
            .annotate(nome_sem_espacos=Trim('nome'))
            .filter(criterios, membro=False)
        )
        ids_nao_membros = set(nao_membros.values_list('id', flat=True))

        if not ids_nao_membros:
            return

        if ata.presidente_da_reuniao_id in ids_nao_membros:
            ata.presidente_da_reuniao = participante
        if ata.secretario_da_reuniao_id in ids_nao_membros:
            ata.secretario_da_reuniao = participante

        ata.save(update_fields=['presidente_da_reuniao', 'secretario_da_reuniao'])
        ata.presentes_na_ata.filter(id__in=ids_nao_membros).delete()

    @classmethod
    def _sincronizar_participante(
        cls,
        ata: Ata,
        cargo_associacao: str,
        registro: CargoComposicaoVacancia,
        historico_ativo: bool,
    ) -> Participante:
        cargo = Cargos(cargo_associacao).label

        # Identifica se o cargo pertence ao conselho fiscal.
        cargos_conselho = {
            codigo for codigo, _ in Cargos.choices[9:]
        }

        dados = cls._dados_participante(registro)        

        participante = ata.presentes_na_ata.filter(membro=True, cargo=cargo).first()

        if participante is None:
            return Participante.objects.create(
                ata=ata,
                cargo=cargo,
                membro=True,
                conselho_fiscal=(cargo_associacao in cargos_conselho),
                **dados
            )            

        mesma_pessoa = (
            participante.vago == dados['vago'] and
            participante.identificacao == dados['identificacao'] and
            participante.nome == dados['nome']
        )

        if mesma_pessoa:
            dados.pop('presente')
        else:
            cls._limpar_referencias_ata(ata, [participante], historico_ativo)

        for campo, valor in dados.items():
            setattr(participante, campo, valor)
            participante.save(update_fields=[*dados, 'alterado_em'])

        return participante