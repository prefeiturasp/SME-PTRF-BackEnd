from datetime import date

from django.db.models import Q

from sme_ptrf_apps.paa.models.ata_paa import AtaPaa
from sme_ptrf_apps.paa.models.participante_ata_paa import ParticipanteAtaPaa
from sme_ptrf_apps.mandatos.models import ComposicaoVacancia, CargoComposicaoVacancia, OcupanteCargo


class SincronizarParticipanteAtaPaaService:
    """Reflete nas atas do PAA as alterações da timeline de um cargo (Histórico de Membros v2)."""

    @classmethod
    def sincroniza_participante_nas_atas_paa(
        cls,
        composicao_vacancia: ComposicaoVacancia,
        cargo_associacao: str,
        data_inicio: date,
        data_fim: date,
    ) -> None:
        """Atualiza o participante do cargo nas atas do PAA não geradas com reunião no intervalo.

        Para cada ata, busca o registro do cargo vigente na data da reunião (o mesmo que o
        endpoint composicao-por-data retorna) e sobrescreve o participante daquele cargo.
        Os demais participantes da ata não são alterados.
        """
        atas_paa = AtaPaa.objects.filter(
            paa__associacao=composicao_vacancia.associacao,
        ).com_data_reuniao_na_data_entre(
            data_inicio_no_cargo=data_inicio,
            data_fim_no_cargo=data_fim,
        )

        cargo_label = CargoComposicaoVacancia(cargo_associacao=cargo_associacao).get_cargo_associacao_display()

        for ata_paa in atas_paa:
            # Ata sem membros ainda será preenchida pelo front a partir da composição
            if not ata_paa.presentes_na_ata_paa.filter(membro=True).exists():
                continue

            registro = CargoComposicaoVacancia.objects.filter(
                composicao=composicao_vacancia,
                cargo_associacao=cargo_associacao,
                data_inicio_no_cargo__lte=ata_paa.data_reuniao,
                data_fim_no_cargo__gte=ata_paa.data_reuniao,
            ).select_related('ocupante_do_cargo').first()

            if not registro:
                continue

            participante = cls._atualiza_participante_do_cargo(ata_paa, cargo_label, registro)

            if registro.ocupante_do_cargo:
                cls._remove_ocupante_como_nao_membro(ata_paa, participante, registro.ocupante_do_cargo)

    @classmethod
    def _atualiza_participante_do_cargo(
        cls,
        ata_paa: AtaPaa,
        cargo_label: str,
        registro: CargoComposicaoVacancia,
    ) -> ParticipanteAtaPaa:
        """Sobrescreve o participante do cargo com o registro vigente na data da reunião.

        Quando a pessoa do cargo muda (ou o cargo fica vago), deixa de ser presidente/secretário
        da reunião e a presença volta ao padrão. Se continua a mesma pessoa, a presença
        marcada pelo usuário é mantida.
        """
        dados = cls._dados_participante(registro)

        participante = ata_paa.presentes_na_ata_paa.filter(membro=True, cargo=cargo_label).first()

        if participante is None:
            return ParticipanteAtaPaa.objects.create(ata_paa=ata_paa, membro=True, cargo=cargo_label, **dados)

        mesma_pessoa = (
            participante.vago == dados['vago'] and
            participante.identificacao == dados['identificacao'] and
            participante.nome == dados['nome']
        )

        if mesma_pessoa:
            dados.pop('presente')
        else:
            cls._remove_participante_de_presidente_e_secretario(ata_paa, participante)

        for campo, valor in dados.items():
            setattr(participante, campo, valor)
        participante.save(update_fields=[*dados, 'alterado_em'])

        return participante

    @classmethod
    def _remove_participante_de_presidente_e_secretario(
        cls,
        ata_paa: AtaPaa,
        participante: ParticipanteAtaPaa,
    ) -> None:
        """Desvincula o participante da presidência/secretaria da reunião, se for o caso.

        Ao salvar a ata, presidente/secretário são gravados tanto nas FKs quanto nos campos
        textuais (nome + cargo), com ou sem as flags de histórico de membros. Por isso os
        dois são limpos sempre, cada um pelo seu critério.
        """
        campos = [
            *cls._limpa_fks_da_reuniao(ata_paa, participante),
            *cls._limpa_campos_legados_da_reuniao(ata_paa, participante),
        ]

        if campos:
            ata_paa.save(update_fields=[*campos, 'alterado_em'])

    @staticmethod
    def _limpa_fks_da_reuniao(ata_paa: AtaPaa, participante: ParticipanteAtaPaa) -> list[str]:
        """Limpa presidente/secretário da reunião (FKs) que apontam para o participante."""
        campos = []
        if ata_paa.presidente_da_reuniao_id == participante.id:
            ata_paa.presidente_da_reuniao = None
            campos.append('presidente_da_reuniao')
        if ata_paa.secretario_da_reuniao_id == participante.id:
            ata_paa.secretario_da_reuniao = None
            campos.append('secretario_da_reuniao')
        return campos

    @staticmethod
    def _limpa_campos_legados_da_reuniao(ata_paa: AtaPaa, participante: ParticipanteAtaPaa) -> list[str]:
        """Limpa presidente/secretário da reunião (texto) com o mesmo nome e cargo do participante."""
        cargo = (participante.cargo or '').lower()
        campos = []

        if (
            ata_paa.presidente_reuniao == participante.nome and
            (ata_paa.cargo_presidente_reuniao or '').lower() == cargo
        ):
            ata_paa.presidente_reuniao = ''
            ata_paa.cargo_presidente_reuniao = ''
            campos += ['presidente_reuniao', 'cargo_presidente_reuniao']

        if (
            ata_paa.secretario_reuniao == participante.nome and
            (ata_paa.cargo_secretaria_reuniao or '').lower() == cargo
        ):
            ata_paa.secretario_reuniao = ''
            ata_paa.cargo_secretaria_reuniao = ''
            campos += ['secretario_reuniao', 'cargo_secretaria_reuniao']

        return campos

    @staticmethod
    def _remove_ocupante_como_nao_membro(
        ata_paa: AtaPaa,
        participante: ParticipanteAtaPaa,
        ocupante: OcupanteCargo,
    ) -> None:
        """Remove o ocupante da lista de não membros da ata, mantendo-o apenas no cargo.

        Se o registro removido era o presidente ou secretário da reunião, o vínculo é
        transferido para o participante do cargo.
        """
        identificacoes = [i for i in (ocupante.codigo_identificacao, ocupante.cpf_responsavel) if i]

        criterios = Q()
        if identificacoes:
            criterios |= Q(identificacao__in=identificacoes)
        if ocupante.nome:
            criterios |= Q(nome=ocupante.nome)

        if not criterios:
            return

        nao_membros = ata_paa.presentes_na_ata_paa.filter(criterios, membro=False)
        ids_nao_membros = set(nao_membros.values_list('id', flat=True))

        if not ids_nao_membros:
            return

        if ata_paa.presidente_da_reuniao_id in ids_nao_membros:
            ata_paa.presidente_da_reuniao = participante
        if ata_paa.secretario_da_reuniao_id in ids_nao_membros:
            ata_paa.secretario_da_reuniao = participante

        ata_paa.save(update_fields=['presidente_da_reuniao', 'secretario_da_reuniao'])
        nao_membros.delete()

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
