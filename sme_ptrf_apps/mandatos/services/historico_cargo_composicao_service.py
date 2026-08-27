from datetime import date, timedelta
from django.db import transaction
from typing import List
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
    """ Nenhum outr módulo monta a quesry de 'quem está ativo'/'está ativo' """
    # D-N onde N = dias. Por padrão = 1
    DIAS_ANTECEDENCIA_SAIDA = 1

    @staticmethod
    def get_or_create_composicao_vacancia(associacao: Associacao, mandato: Mandato) -> ComposicaoVacancia:
        with transaction.atomic():
            composicao_vacancia, _ = ComposicaoVacancia.objects.get_or_create(
                associacao=associacao,
                mandato=mandato,
            )
            return composicao_vacancia

    @staticmethod
    def get_composicao_vacancia_por_uuid_ou_associacao_e_data(
        composicao_uuid: str = None,
        associacao_uuid: str = None,
        data: date = None,
    ) -> ComposicaoVacancia | None:
        """ Resolve a ComposicaoVacancia por uuid direto (caminho rápido, quando o
        front já tem em mãos) ou por associacao_uuid + data (mesmos
        parâmetros que a v1 já usa hoje em cargos-composicao/composicao-por-data/,
        sem exigir o uuid da ComposicaoVacancia de antemão).

        Só existe uma ComposicaoVacancia por (associacao, mandato)
        e mandatos não se sobrepõem no tempo.

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
                             data: date) -> CargoComposicaoVacancia:
        """ Query que verifica 'quem ocupa?' e 'está vago?' """
        return CargoComposicaoVacancia.objects.filter(
            composicao=composicao_vacancia,
            cargo_associacao=cargo_associacao,
            data_inicio_no_cargo__lte=data,
            data_fim_no_cargo__gte=data
        ).first()

    @classmethod
    def get_snapshot_da_composicao_em_data(cls, composicao_vacancia: ComposicaoVacancia, data: date) -> dict:
        return {
            cargo_associacao: cls.get_ocupante_em_data(composicao_vacancia, cargo_associacao, data)
            for cargo_associacao, _ in Cargos.choices
        }

    @staticmethod
    def get_datas_de_alteracao_da_composicao(composicao_vacancia: ComposicaoVacancia) -> List[date]:
        """ Listagem de Datas de Alteração da Composição - permitirá navegar entre alterações de um mandato """
        return list(
            CargoComposicaoVacancia.objects.filter(composicao=composicao_vacancia)
            .values_list('data_inicio_no_cargo', flat=True)
            .distinct()
            .order_by('data_inicio_no_cargo')
        )

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
        """ Desfaz uma entrada como se nunca tivesse acontecido. Só permitido no registro
        vigente (ninguém entrou depois). Restaura quem veio antes (ocupante substituído
        ou vacância) de volta ao estado anterior a esta entrada. """
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
        """ Reverte uma saída
            - volta data_fim_no_cargo para a data final do mandato vigente, de novo
            - remove vacancia aberta associada, se existir.
            - Mas é bloqueado se já existir um sucessor direto (substituido_por preenchido).
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
        """ Corrige data de saída já registrada:
         - reverte para vigente (mesma regra de cancelar saida). Bloqueado se já existe sucessor direto
         - registra a saída de novo com a data corrigida.
         - todas as validações de saída rodam novamente sobre a nova data
           """

        cls.cancelar_saida(cargo_composicao_vacancia)
        return cls.registrar_saida(cargo_composicao_vacancia, nova_data_saida)

    @staticmethod
    def get_timeline_do_cargo(
            composicao_vacancia: ComposicaoVacancia, cargo_associacao: str) -> List[CargoComposicaoVacancia]:
        """ Retorna todo o histórico (ocupados e vagos) de um cargo, ordenado cronologicamente"""
        return list(
            CargoComposicaoVacancia.objects.filter(
                composicao=composicao_vacancia,
                cargo_associacao=cargo_associacao
            ).order_by('data_inicio_no_cargo')
        )

    @classmethod
    def monta_cargos_da_composicao(cls, composicao_vacancia: ComposicaoVacancia, data: date) -> dict:
        """ Monta os cargos da composição
        Args:
            composicao_vacancia: composição cujos cargos serão montados.
            data: data de referência do snapshot (padrão hoje).

        Returns:
            Dicionário com as chaves diretoria_executiva (9 itens) e "conselho fiscal" (5 itens),
            um item por cargo na ordem de Cargos.choices
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
                mandato_data_final=composicao_vacancia.mandato.data_final
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
            registro: CargoComposicaoVacancia,
            cargo_associacao: str,
            label: str,
            eh_composicao_vigente: bool,
            mandato_data_final: date) -> dict:
        """ Monta um item do cargo da composição
        Args:
            registro: CargoComposicaoVacancia do cargo na data de referencia
            cargo_associacao: cargo associado, usado quando registro é None
            label: label completo do cargo (Cargo.choices) usado pra derivar o label curto.
            eh_composicao_vigente: se o mandato desta composição é o mandato vigente
            mandato_data_final: data de saída do mandato

        Returns:
            Dicionário com as chaves cargo_associacao, label, eh_composicao_vigente, ocupantes e vagas
        """
        # representa cargo sem ocupante
        cargo_vazio = registro is None or registro.ocupante_do_cargo_id is None
        # representa cargo vigente sem ocupante
        cargo_vazio_vigente = (
            registro and registro.ocupante_do_cargo_id is None and
            registro.data_fim_no_cargo == mandato_data_final
        )

        ocupante = registro.ocupante_do_cargo if registro and registro.ocupante_do_cargo_id else None
        ocupante_vigente = bool(registro) and not cargo_vazio and registro.data_fim_no_cargo == mandato_data_final
        ocupante_substitui = (
            registro.substituto_imediato.ocupante_do_cargo.nome if registro and registro.substituto else None
        )
        ocupante_substituido_por = (
            registro.substituido_por.ocupante_do_cargo.nome if registro and registro.substituido_por else None
        )

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
            # Não existe "composição passada" na v2 (uma única composição por mandato) - sempre None
            "data_fim_no_cargo_composicao_mais_recente": None,
            "eh_composicao_vigente": eh_composicao_vigente,
            "substituto": registro.substituto if registro else None,
            "tag_substituto": (
                f'Novo membro em {registro.data_inicio_no_cargo.strftime("%d/%m/%Y")}'
                if registro and registro.substituto else None
            ),
            "substituido": registro.substituido if registro else None,
            # Diferente da v1 (usa a data final da composição inteira pra montar essa tag) -
            # aqui usa data_fim_no_cargo do próprio registro, a data real da substituição.
            "tag_substituido": (
                f'Substituído em {registro.substituido_por.data_inicio_no_cargo.strftime("%d/%m/%Y")}'
                if registro and registro.substituido_por else None
            ),
            "ocupante_substitui": ocupante_substitui,
            "ocupante_substituido_por": ocupante_substituido_por,
            "cargo_vago": cargo_vazio,
            "cargo_vago_vigente": cargo_vazio_vigente,
            "ocupante_vigente": ocupante_vigente,
            "ocupante_editavel": cargo_vazio,
            "data_final_editavel": not cargo_vazio,
            "vago_desde": registro.data_inicio_no_cargo if registro and registro.ocupante_do_cargo_id is None else None,
        }

    @classmethod
    @transaction.atomic
    def editar_ocupante(cls, cargo_composicao_vacancia: CargoComposicaoVacancia,
                        dados_ocupante: dict = None) -> CargoComposicaoVacancia:
        """ Edita ocupante de um registro existente.

        Não altera `cargo_associacao` fonte base do registro, nem datas ou vínculo em si
        Essas açoes passam exclusivamente pelos fluxo de registrar entrada/saída/cancelar/corrigir

        Args:
            `cargo_composicao_vacancia`: CargoComposicaoVacancia a ser editado
            `dados_ocupante`: dados do ocupante a serem editados

        Raises:
            CargoComposicaoVacanciaValidationError: se o cargo estiver vago
        """
        ValidatorCargoVazio.validar(cargo_composicao_vacancia)

        ocupante: OcupanteCargo = cargo_composicao_vacancia.ocupante_do_cargo

        for campo, valor in dados_ocupante.items():
            setattr(ocupante, campo, valor)
        ocupante.save()

        return cargo_composicao_vacancia
