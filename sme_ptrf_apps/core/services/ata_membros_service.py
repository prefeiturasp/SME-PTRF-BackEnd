
from datetime import date

from django.db import transaction

from sme_ptrf_apps.core.models import Ata, Participante
from waffle import get_waffle_flag_model
from sme_ptrf_apps.mandatos.choices import (
    CargoComposicaoVacanciaChoices as Cargos,
)
from sme_ptrf_apps.mandatos.models import (
    CargoComposicaoVacancia,
    ComposicaoVacancia,
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

        historico_v2 = cls.flags.objects.filter(
            name="historico-de-membros-v2",
            everyone=True,
        ).exists()

        if not historico_v2:
            return

        if data_inicio > data_fim:
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

        # Recupera a timeline do cargo uma única vez.
        registros = list(
            CargoComposicaoVacancia.objects.filter(
                composicao=composicao_vacancia,
                cargo_associacao=cargo_associacao,
                data_inicio_no_cargo__lte=data_fim,
                data_fim_no_cargo__gte=data_inicio,
            )
            .select_related("ocupante_do_cargo")
            .order_by("data_inicio_no_cargo")
        )

        historico_v1 = cls.flags.objects.filter(
            name="historico-de-membros",
            everyone=True,
        ).exists()

        indice = 0

        for ata in atas:
            # Avança pelos registros encerrados antes da ata.
            while (
                indice < len(registros)
                and registros[indice].data_fim_no_cargo
                < ata.data_reuniao
            ): 
                indice += 1

            registro = None

            if indice < len(registros):
                candidato = registros[indice]

                if (
                    candidato.data_inicio_no_cargo
                    <= ata.data_reuniao
                    <= candidato.data_fim_no_cargo
                ):
                    registro = candidato

            cls._sincronizar_participante(
                ata=ata,
                cargo_associacao=cargo_associacao,
                registro=registro,
                historico_ativo=(historico_v1 or historico_v2)
            )


    @staticmethod
    def _sincronizar_participante(
        ata: Ata,
        cargo_associacao: str,
        registro: CargoComposicaoVacancia | None,
        historico_ativo: bool,
    ) -> None:
        cargo = Cargos(cargo_associacao).label

        # Identifica se o cargo pertence ao conselho fiscal.
        cargos_conselho = {
            codigo for codigo, _ in Cargos.choices[9:]
        }

        membros_do_cargo = Participante.objects.filter(
            ata=ata,
            cargo=cargo,
            membro=True,
        )

        def limpar_referencias_ata(membros, flag_historico: bool):
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
                
                for membro in membros:
                    membro_cargo = (membro.cargo or "").lower()
                    ata_cargo_presidente = (ata.cargo_presidente_reuniao or "").lower()
                    ata_cargo_secretaria = (ata.cargo_secretaria_reuniao or "").lower()

                    if (
                        ata.presidente_reuniao == membro.nome
                        and ata_cargo_presidente == membro_cargo
                    ):
                        ata.presidente_reuniao = ""
                        ata.cargo_presidente_reuniao = ""

                        campos_atualizados.update([
                            "presidente_reuniao",
                            "cargo_presidente_reuniao",
                        ])
                    
                    if (
                        ata.secretario_reuniao == membro.nome
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

        # Cargo vago ou inexistente na data da ata.
        if registro is None or registro.ocupante_do_cargo_id is None:
            limpar_referencias_ata(list(membros_do_cargo), historico_ativo)
            membros_do_cargo.delete()
            return

        ocupante = registro.ocupante_do_cargo

        codigo_identificacao = ocupante.codigo_identificacao or ocupante.cpf_responsavel or ""

        # Caso haja um não-membro com mesmo identificador, apaga-o.
        Participante.objects.filter(
            membro=False,
            identificacao=codigo_identificacao
        ).delete()

        participante, criado = Participante.objects.get_or_create(
            ata=ata,
            cargo=cargo,
            membro=True,
            defaults={
                "nome": ocupante.nome,
                "identificacao": codigo_identificacao,
                "conselho_fiscal": (
                    cargo_associacao in cargos_conselho
                ),
            },
        )

        if criado:
            return

        # Limpa as referências apenas quando os dados que
        # identificam o participante forem alterados.
        if (
            participante.nome != ocupante.nome
            or participante.identificacao != codigo_identificacao
        ):
            limpar_referencias_ata([participante], historico_ativo)

        participante.nome = ocupante.nome
        participante.identificacao = codigo_identificacao
        participante.conselho_fiscal = (
            cargo_associacao in cargos_conselho
        )

        participante.save(
            update_fields=[
                "nome",
                "identificacao",
                "conselho_fiscal",
            ]
        )
