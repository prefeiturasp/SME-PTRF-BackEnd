from datetime import date, timedelta

from django.db import transaction
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.mandatos.models import Mandato
from sme_ptrf_apps.mandatos.models import ComposicaoVacancia, CargoComposicaoVacancia, OcupanteCargo
from sme_ptrf_apps.mandatos.choices import CargoComposicaoVacanciaChoices as Cargos
from sme_ptrf_apps.mandatos.services.validators.validators import (
    ValidatorCargoVazio,
    ValidatorSemGapNaTimelineDoCargo,
)
from sme_ptrf_apps.mandatos.services.validators.validators_entrada import (
    ValidatorEntradaDatasDentroDoMandato,
    ValidatorEntradaDataNaoFutura,
    ValidatorEntradaCargoSemOcupanteVigente,
    ValidatorEntradaSemConflitoDeDatas,
    ValidatorEntradaOcupanteNaoEstaEmOutroCargo,
    ValidatorEntradaSemDuplicidadeDeOcupante,
)

from sme_ptrf_apps.mandatos.services.validators.validators_saida import (
    ValidatorSaidaDataNaoAnteriorAoCargo,
    ValidatorSaidaOcupanteVigente,
    ValidatorSaidaDataNaoPosteriorAoMandato,
    ValidatorSaidaDataNaoFutura,
    ValidatorSaidaCancelarSaidaRegistroEncerrado,
    ValidatorSaidaCancelarSaidaSemSucessor,
)
from .mandato_vacancia_service import ServicoMandatoVigenteVacancia


class ServicoHistoricoCargoComposicao:
    """Ponto único de leitura/escrita da timeline de cargos da composição (Histórico de Membros v2)."""
    # D-N onde N = dias. Por padrão = 1
    DIAS_ANTECEDENCIA_SAIDA = 1

    @staticmethod
    def get_or_create_composicao_vacancia(associacao: Associacao, mandato: Mandato) -> ComposicaoVacancia:
        """Retorna a ComposicaoVacancia do par (associacao, mandato), criando-a se não existir."""
        with transaction.atomic():
            composicao_vacancia, _ = ComposicaoVacancia.objects.get_or_create(
                associacao=associacao,
                mandato=mandato,
            )
            return composicao_vacancia

    @staticmethod
    def get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        composicao_uuid: str | None = None,
        associacao_uuid: str | None = None,
        data: date | None = None,
    ) -> ComposicaoVacancia | None:
        """Resolve a ComposicaoVacancia por uuid direto ou por associacao_uuid + data.

        O uuid direto é o caminho rápido (quando o front já o tem em mãos); associacao_uuid
        + data usa os mesmos parâmetros que a v1 já expõe em composicao-por-data/, sem exigir
        o uuid de antemão. Só existe uma ComposicaoVacancia por (associacao, mandato) e
        mandatos não se sobrepõem no tempo.

        Args:
            composicao_uuid: uuid da ComposicaoVacancia, se já conhecido.
            associacao_uuid: uuid da associação (usado só se composicao_uuid não vier).
            data: data de referência (usado só se composicao_uuid não vier).

        Returns:
            A ComposicaoVacancia encontrada, ou None se nenhum critério bater.
        """
        if composicao_uuid:
            return ComposicaoVacancia.objects.filter(uuid=composicao_uuid).first()

        if associacao_uuid and data:
            return ComposicaoVacancia.objects.filter(
                associacao__uuid=associacao_uuid,
                mandato__data_inicial__lte=data,
                mandato__data_final__gte=data,
            ).first()

        return None

    @staticmethod
    def get_ocupante_em_data(composicao_vacancia: ComposicaoVacancia,
                             cargo_associacao: str,
                             data: date) -> CargoComposicaoVacancia | None:
        """Retorna o registro do cargo que cobre a data (ocupado ou vago), ou None."""
        return CargoComposicaoVacancia.objects.filter(
            composicao=composicao_vacancia,
            cargo_associacao=cargo_associacao,
            data_inicio_no_cargo__lte=data,
            data_fim_no_cargo__gte=data
        ).first()

    @classmethod
    def get_snapshot_da_composicao_em_data(cls, composicao_vacancia: ComposicaoVacancia, data: date) -> dict:
        """Retorna, por cargo do catálogo, o registro vigente na data (ou None se vago/inexistente)."""
        return {
            cargo_associacao: cls.get_ocupante_em_data(composicao_vacancia, cargo_associacao, data)
            for cargo_associacao, _ in Cargos.choices
        }

    @staticmethod
    def _bloco_cronologico_intervalo_datas(datas: list[tuple[date, date]]) -> list[tuple[date, date]]:
        # maior data_fim_no_cargo entre todas as datas - teto dos intervalos gerados
        data_final = max(fim for _, fim in datas)

        # 1º grupo de cortes: o início de cada data, de qualquer cargo
        cortes = {inicio for inicio, _ in datas}  # usando set para evitar duplicatas
        # 2º grupo de cortes: o dia seguinte ao fim de cada data
        cortes.update(
            fim + timedelta(days=1)
            for _, fim in datas
            if fim + timedelta(days=1) <= data_final
        )
        # ordena cronologicamente
        cortes_ordenados = sorted(cortes)

        # cada corte vira o início de um marco; o fim do marco é a véspera do
        # próximo corte, ou o teto (data_final) quando for o último corte da lista
        return [
            (
                inicio,
                cortes_ordenados[indice + 1] - timedelta(days=1)
                if indice + 1 < len(cortes_ordenados)
                else data_final
            )
            for indice, inicio in enumerate(cortes_ordenados)
        ]

    @staticmethod
    def get_datas_de_alteracao_da_composicao(composicao_vacancia: ComposicaoVacancia) -> list[tuple[date, date]]:
        """Retorna os intervalos cronológicos, sem sobreposição, em que a composição
        permaneceu inalterada, em ordem crescente para consulta.

        São os "marcos" de navegação entre alterações de um mandato. Os registros de
        cargos diferentes têm vigências independentes e se sobrepõem entre si (ex.: um
        cargo pode começar em 01/01 e só mudar de novo em 31/07, enquanto outro começa
        também em 01/01 mas muda em 31/08) - por isso não dá pra usar os pares
        (data_inicio_no_cargo, data_fim_no_cargo) de cada registro diretamente como
        intervalo de um marco. Em vez disso, cada início de registro (de qualquer cargo)
        e o dia seguinte a cada fim marcam um novo corte na linha do tempo; os intervalos
        entre cortes consecutivos são os marcos em que nada mudou em nenhum cargo.
        """
        # busca todos os registros/datas (de todos os cargos) da composição, já como
        # tuplas (data_inicio_no_cargo, data_fim_no_cargo) - sem instanciar o model
        datas = list(
            CargoComposicaoVacancia.objects.filter(composicao=composicao_vacancia)
            .values_list('data_inicio_no_cargo', 'data_fim_no_cargo')
        )

        # composição sem nenhum registro em nenhum cargo: não há marco a montar
        if not datas:
            return []

        return ServicoHistoricoCargoComposicao._bloco_cronologico_intervalo_datas(datas)

    @classmethod
    @transaction.atomic
    def registrar_entrada(cls,
                          composicao_vacancia: ComposicaoVacancia,
                          ocupante_do_cargo: OcupanteCargo,
                          cargo_associacao: str,
                          data_entrada: date) -> CargoComposicaoVacancia:
        mandato: Mandato = composicao_vacancia.mandato

        dia_anterior_a_entrada: date = data_entrada - timedelta(days=1)

        # select_for_update() - trava antes de validar/decidir,
        # evita corrida entre dois registrar_entrada concorrentes no mesmo cargo/vacancia.
        registros_do_cargo = CargoComposicaoVacancia.objects.select_for_update().filter(
            composicao=composicao_vacancia,
            cargo_associacao=cargo_associacao
        )

        # Aplica Validações de Entrada
        ValidatorEntradaDatasDentroDoMandato.validar(mandato=mandato, data_inicio=data_entrada)
        ValidatorEntradaDataNaoFutura.validar(data_entrada=data_entrada)
        ValidatorEntradaCargoSemOcupanteVigente.validar(registros_do_cargo=registros_do_cargo, mandato=mandato)
        ValidatorEntradaSemConflitoDeDatas.validar(
            registros_do_cargo=registros_do_cargo,
            data_inicio=data_entrada,
            data_fim=mandato.data_final,
        )
        ValidatorEntradaOcupanteNaoEstaEmOutroCargo.validar(
            composicao_vacancia=composicao_vacancia,
            ocupante_do_cargo=ocupante_do_cargo,
            cargo_associacao=cargo_associacao,
            data_inicio=data_entrada,
            data_fim=mandato.data_final,
        )
        ValidatorEntradaSemDuplicidadeDeOcupante.validar(
            composicao_vacancia=composicao_vacancia,
            ocupante_do_cargo=ocupante_do_cargo,
            mandato=mandato,
        )

        # é a primeira entrada desse cargo (nunca teve nenhum registro) - precisa saber
        # antes de criar o novo registro, se não, a checagem sempre dá False.
        # Diferente do gap pós-saída (sempre materializado por registrar_saida), o gap
        # entre o início do mandato e a primeira entrada é implícito
        # materializamos aqui pra unificar a representação de "vago" em toda a API
        primeira_entrada_do_cargo = not registros_do_cargo.exists()

        # busca vacancia sem ocupante(aberta) - Vacancia aberta é uma vacancia sem ocupante que representa o vago
        vacancia_aberta = registros_do_cargo.filter(
            ocupante_do_cargo__isnull=True,
            data_inicio_no_cargo__lte=data_entrada,
            data_fim_no_cargo__gte=data_entrada
        ).first()

        if vacancia_aberta:
            if vacancia_aberta.data_inicio_no_cargo == data_entrada:
                # Remove para adicionar nova entrada - representa a substituição direta
                vacancia_aberta.delete()
            else:
                # altera a data fim da vacância aberta (representa o gap)
                vacancia_aberta.data_fim_no_cargo = dia_anterior_a_entrada
                vacancia_aberta.save()
        elif primeira_entrada_do_cargo and data_entrada > mandato.data_inicial:
            # Primeira entrada do cargo, começando depois do início do mandato
            # cria um vago entre o início do mandato e a primeira entrada
            CargoComposicaoVacancia.objects.create(
                composicao=composicao_vacancia,
                ocupante_do_cargo=None,
                cargo_associacao=cargo_associacao,
                data_inicio_no_cargo=mandato.data_inicial,
                data_fim_no_cargo=dia_anterior_a_entrada,
            )

        # Cria novo registro de cargo vacância
        novo_registro = CargoComposicaoVacancia.objects.create(
            composicao=composicao_vacancia,
            ocupante_do_cargo=ocupante_do_cargo,
            cargo_associacao=cargo_associacao,
            data_inicio_no_cargo=data_entrada,
            data_fim_no_cargo=mandato.data_final
        )

        # verifica se o registro anterior termina exatamente no dia anterior (sem gap)
        registro_anterior = registros_do_cargo.filter(
            ocupante_do_cargo__isnull=False,
            data_fim_no_cargo=dia_anterior_a_entrada
        ).first()

        if registro_anterior:
            # se o registro anterior é imediatomente anterior(D-N), vincula o substituto
            registro_anterior.substituido_por = novo_registro
            registro_anterior.save()

        # Validador de verificação de Gaps
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=composicao_vacancia,
            cargo_associacao=cargo_associacao,
            mandato=mandato,
        )

        return novo_registro

    @classmethod
    @transaction.atomic
    def registrar_saida(cls,
                        cargo_composicao_vacancia: CargoComposicaoVacancia,
                        data_saida: date) -> CargoComposicaoVacancia:
        mandato: Mandato = cargo_composicao_vacancia.composicao.mandato

        data_fim: date = data_saida - timedelta(days=cls.DIAS_ANTECEDENCIA_SAIDA)

        # Aplica Validações de Saída
        ValidatorSaidaOcupanteVigente.validar(cargo_composicao_vacancia=cargo_composicao_vacancia)
        ValidatorSaidaDataNaoPosteriorAoMandato.validar(data_saida=data_saida, mandato=mandato)
        ValidatorSaidaDataNaoFutura.validar(data_saida=data_saida, mandato=mandato)
        ValidatorSaidaDataNaoAnteriorAoCargo.validar(
            data_saida=data_fim,
            cargo_composicao_vacancia=cargo_composicao_vacancia)

        # registra a data fim da vacancia (D-N)
        cargo_composicao_vacancia.data_fim_no_cargo = data_fim
        cargo_composicao_vacancia.save()

        # Sempre cria uma vacância aberta (inicia no dia seguinte ao fim da vacância anterior)
        data_inicio_vacancia_aberta = data_fim + timedelta(days=1)
        CargoComposicaoVacancia.objects.create(
            composicao=cargo_composicao_vacancia.composicao,
            ocupante_do_cargo=None,  # (representa o vago)
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            data_inicio_no_cargo=data_inicio_vacancia_aberta,
            data_fim_no_cargo=mandato.data_final
        )

        # Validador de verificação de Gaps
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=cargo_composicao_vacancia.composicao,
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            mandato=mandato,
        )

        return cargo_composicao_vacancia

    @classmethod
    @transaction.atomic
    def cancelar_entrada(cls, cargo_composicao_vacancia: CargoComposicaoVacancia) -> None:
        """Desfaz uma entrada como se nunca tivesse acontecido.

        Só permitido no registro vigente (ninguém entrou depois). Restaura quem veio antes
        (ocupante substituído ou vacância) ao estado anterior a esta entrada.
        """
        mandato = cargo_composicao_vacancia.composicao.mandato

        # reaproveita a mesma checagem de "é o vigente"
        ValidatorSaidaOcupanteVigente.validar(cargo_composicao_vacancia)

        anterior = CargoComposicaoVacancia.objects.filter(
            composicao=cargo_composicao_vacancia.composicao,
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            data_fim_no_cargo=cargo_composicao_vacancia.data_inicio_no_cargo - timedelta(days=1),
        ).first()

        if anterior:
            anterior.data_fim_no_cargo = mandato.data_final
            anterior.substituido_por = None
            anterior.save()
        else:
            # era a própria primeira entrada do cargo, sem nada antes dela
            CargoComposicaoVacancia.objects.create(
                composicao=cargo_composicao_vacancia.composicao,
                cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
                ocupante_do_cargo=None,
                data_inicio_no_cargo=mandato.data_inicial,
                data_fim_no_cargo=mandato.data_final,
            )

        cargo_composicao_vacancia.delete()

        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=cargo_composicao_vacancia.composicao,
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            mandato=mandato,
        )

    @classmethod
    def cancelar_saida(cls, cargo_composicao_vacancia: CargoComposicaoVacancia) -> CargoComposicaoVacancia:
        """Reverte uma saída.

        Volta data_fim_no_cargo para a data final do mandato e remove a vacância aberta
        associada, se existir. Bloqueado se já existir um sucessor direto (substituido_por
        preenchido).
        """
        mandato: Mandato = cargo_composicao_vacancia.composicao.mandato

        # aplica validators
        ValidatorSaidaCancelarSaidaRegistroEncerrado.validar(cargo_composicao_vacancia, mandato)
        ValidatorSaidaCancelarSaidaSemSucessor.validar(cargo_composicao_vacancia)

        # Remove a vacancia aberta associada - se os validators passaram então não há sucessor,
        # então, se existir vaga para esse cargo só pode ser a criada por essa saída.
        # Neste design, só deve haver uma vaga aberta por cargo x mandato.
        CargoComposicaoVacancia.objects.filter(
            composicao=cargo_composicao_vacancia.composicao,
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            ocupante_do_cargo__isnull=True,
            data_fim_no_cargo=mandato.data_final
        ).delete()

        cargo_composicao_vacancia.data_fim_no_cargo = mandato.data_final
        cargo_composicao_vacancia.save()

        # Validador de verificação de Gaps
        ValidatorSemGapNaTimelineDoCargo.validar(
            composicao_vacancia=cargo_composicao_vacancia.composicao,
            cargo_associacao=cargo_composicao_vacancia.cargo_associacao,
            mandato=mandato,
        )

        return cargo_composicao_vacancia

    @classmethod
    def corrigir_data_saida(cls,
                            cargo_composicao_vacancia: CargoComposicaoVacancia,
                            nova_data_saida: date) -> CargoComposicaoVacancia:
        """Corrige a data de uma saída já registrada.

        Reverte o registro para vigente (mesma regra de cancelar_saida, bloqueado se já
        existe sucessor direto) e registra a saída de novo com a data corrigida. Todas as
        validações de saída rodam de novo sobre a nova data.
        """
        cls.cancelar_saida(cargo_composicao_vacancia)
        return cls.registrar_saida(cargo_composicao_vacancia, nova_data_saida)

    @staticmethod
    def get_timeline_do_cargo(
            composicao_vacancia: ComposicaoVacancia, cargo_associacao: str) -> list:
        """Retorna todo o histórico (ocupados e vagos) de um cargo, ordenado cronologicamente."""

        cargos = CargoComposicaoVacancia.objects.filter(
            composicao=composicao_vacancia,
            cargo_associacao=cargo_associacao
        ).order_by('data_inicio_no_cargo')

        timeline = []
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
        eh_composicao_vigente = composicao_vacancia.mandato_id == (mandato_vigente.id if mandato_vigente else None)
        for cargo_composicao_vacancia in cargos:
            timeline.append(
                ServicoHistoricoCargoComposicao()._monta_item_do_cargo(
                    registro=cargo_composicao_vacancia,
                    cargo_associacao=cargo_associacao,
                    label=Cargos(cargo_associacao).label,
                    eh_composicao_vigente=eh_composicao_vigente,
                    mandato_data_final=cargo_composicao_vacancia.composicao.mandato.data_final,
                    data_consulta_no_cargo=None
                )
            )
        return timeline

    @classmethod
    def get_timeline_consolidada_da_composicao(cls, composicao_vacancia: ComposicaoVacancia) -> dict:
        """Monta, numa única leitura ao banco, a timeline completa (todos os registros,
        ocupados e vagos) de todos os cargos da composição — pensado para servir a
        navegação por data no frontend sem nenhuma requisição adicional.

        Com todos os registros da composição já em memória, eh_primeiro_ocupante,
        eh_ultimo_ocupante e substituto são derivados por cargo (O(n)), eliminando o N+1
        de queries que _monta_item_do_cargo faz quando chamado isoladamente por registro.
        """
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
        eh_composicao_vigente = composicao_vacancia.mandato_id == (mandato_vigente.id if mandato_vigente else None)
        mandato_data_final = composicao_vacancia.mandato.data_final

        registros_por_cargo = {}
        cargos_composicoes = (
            CargoComposicaoVacancia.objects
            .filter(composicao=composicao_vacancia)
            .select_related('ocupante_do_cargo')
            .order_by('cargo_associacao', 'data_inicio_no_cargo')
        )
        # Separar em dicionário por cargo
        for registro in cargos_composicoes:
            registros_por_cargo.setdefault(registro.cargo_associacao, []).append(registro)

        diretoria_executiva = []
        conselho_fiscal = []

        for indice, (cargo_associacao, label) in enumerate(Cargos.choices):
            registros_do_cargo = registros_por_cargo.get(cargo_associacao, [])

            # ids que SÃO um substituto (referenciados como substituido_por por outro registro)
            # TODO: ponto de observação, substituto deve identificar o substituto imediatamente anterior
            ids_que_sao_substituto = {
                registro.substituido_por_id for registro in registros_do_cargo if registro.substituido_por_id
            }
            registros_com_ocupante = [r for r in registros_do_cargo if r.ocupante_do_cargo_id]
            id_primeiro_ocupante = registros_com_ocupante[0].id if registros_com_ocupante else None
            id_ultimo_ocupante = registros_com_ocupante[-1].id if registros_com_ocupante else None

            timeline = [
                cls._monta_item_do_cargo(
                    registro=registro,
                    cargo_associacao=cargo_associacao,
                    label=label,
                    eh_composicao_vigente=eh_composicao_vigente,
                    mandato_data_final=mandato_data_final,
                    data_consulta_no_cargo=None,
                    eh_primeiro_ocupante=registro.id == id_primeiro_ocupante,
                    eh_ultimo_ocupante=registro.id == id_ultimo_ocupante,
                    substituto=registro.id in ids_que_sao_substituto,
                )
                for registro in registros_do_cargo
            ]

            item = {
                'cargo_associacao': cargo_associacao,
                'cargo_associacao_label': label.split(' ')[0],
                'timeline': timeline,
            }

            if indice < 9:
                diretoria_executiva.append(item)
            else:
                conselho_fiscal.append(item)

        return {
            'diretoria_executiva': diretoria_executiva,
            'conselho_fiscal': conselho_fiscal,
        }

    @classmethod
    def monta_cargos_da_composicao(cls, composicao_vacancia: ComposicaoVacancia,
                                   data: date | None) -> dict:
        """Monta os cargos da composição para uma data de referência.

        Args:
            composicao_vacancia: composição cujos cargos serão montados.
            data: data de referência do snapshot. None assume hoje.

        Returns:
            Dicionário com as chaves diretoria_executiva (9 itens) e conselho_fiscal
            (5 itens), um item por cargo na ordem de Cargos.choices.
        """
        data = data or date.today()
        mandato_vigente = ServicoMandatoVigenteVacancia().get_mandato_vigente()
        eh_composicao_vigente = composicao_vacancia.mandato_id == (mandato_vigente.id if mandato_vigente else None)

        snapshot = cls.get_snapshot_da_composicao_em_data(composicao_vacancia, data)

        diretoria_executiva = []
        conselho_fiscal = []

        for indice, (cargo_associacao, label) in enumerate(Cargos.choices):
            registro = snapshot.get(cargo_associacao)
            item = cls._monta_item_do_cargo(
                registro=registro,
                cargo_associacao=cargo_associacao,
                label=label,
                eh_composicao_vigente=eh_composicao_vigente,
                mandato_data_final=composicao_vacancia.mandato.data_final,
                data_consulta_no_cargo=data
            )

            if indice < 9:
                diretoria_executiva.append(item)
            else:
                conselho_fiscal.append(item)

        return {
            'diretoria_executiva': diretoria_executiva,
            'conselho_fiscal': conselho_fiscal
        }

    @staticmethod
    def _monta_item_do_cargo(
            registro: CargoComposicaoVacancia | None,
            cargo_associacao: str,
            label: str,
            eh_composicao_vigente: bool,
            mandato_data_final: date,
            data_consulta_no_cargo: date | None,
            eh_primeiro_ocupante: bool | None = None,
            eh_ultimo_ocupante: bool | None = None,
            substituto: bool | None = None) -> dict:
        """Monta um item do cargo da composição.

        Args:
            registro: registro do cargo na data de referência, ou None se não houver.
            cargo_associacao: cargo, usado quando registro é None.
            label: label completo do cargo (Cargo.choices), usado para derivar o label curto.
            eh_composicao_vigente: se o mandato desta composição é o mandato vigente.
            mandato_data_final: data de fim do mandato.

        Returns:
            Dicionário com os dados do cargo/ocupante no formato consumido pelo frontend.
        """
        # representa cargo sem ocupante
        eh_cargo_vago = registro is None or registro.ocupante_do_cargo_id is None

        # representa cargo vigente sem ocupante
        cargo_vazio_vigente = (
            registro and registro.ocupante_do_cargo_id is None and
            registro.data_fim_no_cargo == mandato_data_final
        )

        # é ocupante inicial: primeiro ocupante que já existiu no cargo, mesmo que antes dele
        # tenha havido um período vago (sem nenhum ocupante anterior)
        if eh_primeiro_ocupante is None:
            eh_primeiro_ocupante = bool(registro) and not eh_cargo_vago and not CargoComposicaoVacancia.objects.filter(
                composicao_id=registro.composicao_id,
                cargo_associacao=registro.cargo_associacao,
                ocupante_do_cargo__isnull=False,
                data_inicio_no_cargo__lt=registro.data_inicio_no_cargo,
            ).exists()

        # é último ocupante: último ocupante que já existiu no cargo, mesmo que depois dele
        # tenha havido um período vago (sem nenhum ocupante posterior)
        if eh_ultimo_ocupante is None:
            eh_ultimo_ocupante = bool(registro) and not eh_cargo_vago and not CargoComposicaoVacancia.objects.filter(
                composicao_id=registro.composicao_id,
                cargo_associacao=registro.cargo_associacao,
                ocupante_do_cargo__isnull=False,
                data_inicio_no_cargo__gt=registro.data_inicio_no_cargo,
            ).exists()

        ocupante = registro.ocupante_do_cargo if registro and registro.ocupante_do_cargo_id else None

        # identifica se o cargo é ocupado e vigente
        ocupante_vigente = bool(registro) and not eh_cargo_vago and registro.data_fim_no_cargo == mandato_data_final

        # Substituto - booleano se é substituto imediato do ocupante anterior
        if substituto is None:
            substituto = registro.substituto if registro else None

        cargo_na_data = bool(registro) and str(registro.data_inicio_no_cargo) == str(data_consulta_no_cargo)
        tag_novo_membro = (
            f'Novo membro em {registro.data_inicio_no_cargo.strftime("%d/%m/%Y")}'
            if registro and cargo_na_data and not eh_primeiro_ocupante else None
        )

        substituido = registro.substituido if registro else None

        # tag de saída: Vacância em DD/MM/YYYY: identifica se cargo tem saída registrada
        tem_saida = bool(registro) and not eh_cargo_vago and not ocupante_vigente
        _data_saida = registro.data_fim_no_cargo if tem_saida else None
        tag_vacancia = f'Vacância em {_data_saida.strftime("%d/%m/%Y")}' if tem_saida else None

        # padrão anterior para manter mínimo impacto de transição para a nova estrutura
        return {
            "id": registro.id if registro else None,
            "uuid": str(registro.uuid) if registro else None,
            "ocupante_do_cargo": {
                "id": ocupante.id if ocupante else None,
                "uuid": str(ocupante.uuid) if ocupante else None,
                "nome": ocupante.nome if ocupante else None,
                "codigo_identificacao": ocupante.codigo_identificacao if ocupante else None,
                "cargo_educacao": ocupante.cargo_educacao if ocupante else None,
                "representacao": ocupante.representacao if ocupante else '',
                "representacao_label": ocupante.get_representacao_display() if ocupante else '',
                "email": ocupante.email if ocupante else None,
                "cpf_responsavel": ocupante.cpf_responsavel if ocupante else None,
                "telefone": ocupante.telefone if ocupante else None,
                "cep": ocupante.cep if ocupante else None,
                "bairro": ocupante.bairro if ocupante else None,
                "endereco": ocupante.endereco if ocupante else None,
            },
            "cargo_associacao": registro.cargo_associacao if registro else cargo_associacao,
            "cargo_associacao_label": label.split(" ")[0],
            "data_inicio_no_cargo": registro.data_inicio_no_cargo if registro else None,
            "data_fim_no_cargo": registro.data_fim_no_cargo if registro else None,
            "eh_composicao_vigente": eh_composicao_vigente,
            "substituto": substituto,
            "tag_novo_membro": tag_novo_membro,
            "substituido": substituido,
            "cargo_vago": eh_cargo_vago,
            "cargo_vago_vigente": cargo_vazio_vigente,
            "cargo_vigente": cargo_vazio_vigente or ocupante_vigente,
            "tem_saida": tem_saida,
            "tag_vacancia": tag_vacancia,
            "ocupante_vigente": ocupante_vigente,
            "eh_primeiro_ocupante": eh_primeiro_ocupante,
            "eh_ultimo_ocupante": eh_ultimo_ocupante,

            # só pode cancelar um ocupante que já saiu (não vigente) e ainda não tem sucessor
            "pode_cancelar_saida": (
                not eh_cargo_vago and not ocupante_vigente and not substituido and eh_ultimo_ocupante
            ),
            "pode_cancelar_entrada": not eh_cargo_vago and ocupante_vigente,
        }

    @classmethod
    @transaction.atomic
    def editar_ocupante(cls, cargo_composicao_vacancia: CargoComposicaoVacancia,
                        dados_ocupante: dict | None) -> CargoComposicaoVacancia:
        """Edita os dados cadastrais do ocupante de um registro existente.

        Não altera cargo_associacao, datas nem vínculo de substituição. Essas mudanças passam
        exclusivamente pelo fluxo de registrar entrada/saída/cancelar/corrigir.

        Args:
            cargo_composicao_vacancia: registro a ser editado.
            dados_ocupante: campos do ocupante a atualizar.

        Raises:
            CargoComposicaoVacanciaValidationError: se o cargo estiver vago.
        """
        ValidatorCargoVazio.validar(cargo_composicao_vacancia)

        ocupante: OcupanteCargo = cargo_composicao_vacancia.ocupante_do_cargo

        for campo, valor in dados_ocupante.items():
            setattr(ocupante, campo, valor)
        ocupante.save()

        return cargo_composicao_vacancia
