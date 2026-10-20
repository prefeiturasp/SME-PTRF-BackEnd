import logging
from typing import Optional

from celery import shared_task

from sme_ptrf_apps.core.models import Unidade, Associacao, MembroAssociacao
from sme_ptrf_apps.mandatos.models import (
    Mandato, SolicitacaoDeMigracao, OcupanteCargo, StatusProcessamento,
    CargoComposicaoVacancia, ComposicaoVacancia
)
from sme_ptrf_apps.mandatos.services.mandato_vacancia_service import ServicoMandatoVigenteVacancia
from sme_ptrf_apps.mandatos.services.historico_cargo_composicao_service import ServicoHistoricoCargoComposicao

logger = logging.getLogger(__name__)


def _retira_ocupantes_da_composicao(composicao: ComposicaoVacancia, mandato: Mandato) -> None:
    """Retira todos os ocupantes dos cargos da composição, pelo fluxo normal de saída/cancelamento.

    Processa só os registros **ocupados** de cada `cargo_associacao`, do mais recente pro mais
    antigo, aplicando a mesma ação que o fluxo normal de retirada usaria:

    - Ocupante vigente (`data_fim_no_cargo == mandato.data_final`): desfaz a entrada via
      `cancelar_entrada` - remove o registro e restaura o predecessor (ou cria vago, se não houver).
    - Ocupante encerrado (`data_fim_no_cargo < mandato.data_final`) sem sucessor direto: desfaz a
      saída via `cancelar_saida` - o registro volta a ser vigente, ficando pronto pra ser tratado
      no próximo passo do laço como um ocupante vigente.

    Como o mais recente é sempre tratado primeiro, um registro encerrado com `substituido_por`
    preenchido nunca chega a ser encontrado nesse estado: seu sucessor (que tem data mais recente)
    já foi removido antes, o que por si só já zera esse `substituido_por` e o promove a vigente.

    Registros vagos nunca são tocados aqui de propósito: `registrar_entrada` já sabe reconciliar
    uma vacância aberta pré-existente (fecha ou apaga, conforme a data de entrada) e o histórico de
    vacância é relevante por si só (ex.: log de movimentação do cargo).

    Evita usar `.delete()` em lote direto na composição: como `substituido_por` é `PROTECT`,
    excluir todos os registros ocupados de uma vez falha com `ProtectedError` sempre que existe uma
    substituição direta na composição (um registro ainda aponta pro outro).

    Args:
        composicao: composição cujos cargos serão esvaziados de ocupantes.
        mandato: mandato da composição, usado para identificar o registro vigente de cada cargo
            (`data_fim_no_cargo == mandato.data_final`).
    """
    cargos_associacao = CargoComposicaoVacancia.objects.filter(
        composicao=composicao, ocupante_do_cargo__isnull=False,
    ).values_list('cargo_associacao', flat=True).distinct()

    for cargo_associacao in cargos_associacao:
        registro = CargoComposicaoVacancia.objects.filter(
            composicao=composicao, cargo_associacao=cargo_associacao, ocupante_do_cargo__isnull=False,
        ).order_by('-data_fim_no_cargo', '-data_inicio_no_cargo').first()

        while registro:
            if registro.data_fim_no_cargo == mandato.data_final:
                ServicoHistoricoCargoComposicao.cancelar_entrada(registro)
                logger.info(f'Cancelando entrada: {registro.cargo_associacao} - {registro.ocupante_do_cargo}')
            elif registro.substituido_por_id is None:
                ServicoHistoricoCargoComposicao.cancelar_saida(registro)
                logger.info(f'Cancelando saída: {registro.cargo_associacao} - {registro.ocupante_do_cargo}')
            else:
                # não deveria acontecer dado o processamento do mais recente pro mais antigo -
                # guarda de segurança pra nunca travar num laço infinito
                logger.warning(
                    f'Registro encerrado com sucessor direto ainda vinculado durante a retirada '
                    f'de ocupantes: {registro}. Pulando.'
                )
                break

            registro = CargoComposicaoVacancia.objects.filter(
                composicao=composicao, cargo_associacao=cargo_associacao, ocupante_do_cargo__isnull=False,
            ).order_by('-data_fim_no_cargo', '-data_inicio_no_cargo').first()


def migrar_associacao_vacancia(associacao: Associacao) -> None:
    """Migra os membros legados (v1) de uma associação para o Histórico de Membros (v2).

    Contraparte de `migrar_associacao` (v1). Para cada `MembroAssociacao` da associação, cria (ou
    reaproveita) o `OcupanteCargo` correspondente e registra sua entrada no cargo via
    `ServicoHistoricoCargoComposicao.registrar_entrada`, usando a data de início do mandato vigente
    como data de entrada.

    Diferente da v1 (que apaga e recria a `Composicao` a cada migração), aqui a `ComposicaoVacancia`
    é reaproveitada - o par (associacao, mandato) é único no model, então recriá-la não faz sentido.
    Os ocupantes atuais são retirados via `_retira_ocupantes_da_composicao` (fluxo normal de
    saída/cancelamento, não `.delete()` em lote) antes de registrar as novas entradas.

    Args:
        associacao: a associação cujos membros legados serão migrados.

    Raises:
        Exception: qualquer falha de validação/negócio ao registrar a entrada de um membro é
            propagada - quem chama (`solicitacao_de_migracao_vacancia_async`) é responsável por
            capturar e registrar o erro na `SolicitacaoDeMigracao`.
    """
    logger.info(f'Migrando Vacância da Associação: {associacao}')

    mandato_vigente: Optional[Mandato] = ServicoMandatoVigenteVacancia().get_mandato_vigente()
    composicao_vigente = ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
        associacao=associacao,
        mandato=mandato_vigente
    )

    logger.info(f'Composição vacância vigente: {composicao_vigente}')

    # Retira os ocupantes atuais dos cargos, pelo fluxo normal de saída/cancelamento (não apaga
    # vago em lote - ver docstring de _retira_ocupantes_da_composicao)
    _retira_ocupantes_da_composicao(composicao_vigente, mandato_vigente)

    # Recupera todos os membros da associacao antigos
    membros_da_associacao = MembroAssociacao.objects.filter(associacao=associacao)

    for membro in membros_da_associacao:

        # Cria Ocupantes do Cargo Histórico de Membros
        ocupante_do_cargo_historico_de_membros, _ = OcupanteCargo.objects.get_or_create(
            nome=membro.nome,
            codigo_identificacao=membro.codigo_identificacao,
            cargo_educacao=membro.cargo_educacao,
            representacao=membro.representacao,
            email=membro.email,
            cpf_responsavel=membro.cpf,
            telefone=membro.telefone,
            cep=membro.cep,
            bairro=membro.bairro,
            endereco=membro.endereco,
            defaults={
                'nome': membro.nome,
                'codigo_identificacao': membro.codigo_identificacao,
                'cargo_educacao': membro.cargo_educacao,
                'representacao': membro.representacao,
                'email': membro.email,
                'cpf_responsavel': membro.cpf,
                'telefone': membro.telefone,
                'cep': membro.cep,
                'bairro': membro.bairro,
                'endereco': membro.endereco,
            },
        )
        # Cria os Cargos Composição Histórico de Membros
        cargo_composicao = ServicoHistoricoCargoComposicao.registrar_entrada(
            composicao_vacancia=composicao_vigente,
            ocupante_do_cargo=ocupante_do_cargo_historico_de_membros,
            cargo_associacao=membro.cargo_associacao,
            data_entrada=mandato_vigente.data_inicial,
        )

        logger.info((
            'Cargo Composição Histórico de Membros (Vacância) criado para ocupante: '
            f'{cargo_composicao} - {ocupante_do_cargo_historico_de_membros}'
        ))

    associacao.migrada_para_historico_de_membros = True
    associacao.save()


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=60000,
    soft_time_limit=60000
)
def solicitacao_de_migracao_vacancia_async(
    solicitacao_uuid: str,
    eol_unidade: Optional[str] = None,
    eol_dre: Optional[str] = None,
) -> None:
    """Task assíncrona que migra associações da v1 para o Histórico de Membros (v2).

    Contraparte de `solicitacao_de_migracao_async` (v1). Filtra as associações a migrar por
    unidade, por DRE, ou todas (quando nenhum dos dois é informado), delegando cada associação
    para `migrar_associacao_vacancia`. Ao final, atualiza `status_processamento`/`log_execucao`
    da `SolicitacaoDeMigracao` com sucesso ou erro - nunca deixa a exceção subir sem tratamento.

    Args:
        solicitacao_uuid: uuid da `SolicitacaoDeMigracao` que originou esta execução.
        eol_unidade: código EOL de uma única unidade a migrar. Tem prioridade sobre `eol_dre`.
        eol_dre: código EOL da DRE cujas unidades serão migradas. Ignorado se `eol_unidade`
            for informado.
    """
    solicitacao = SolicitacaoDeMigracao.by_uuid(solicitacao_uuid)
    solicitacao.inicia_processamento()

    logger.info(f'Iniciando a task solicitacao_de_migracao_vacancia_async para a Solicitação:  {solicitacao}')

    try:
        if eol_unidade:
            qs = Associacao.objects.filter(unidade__codigo_eol=eol_unidade)
        elif eol_dre:
            dre = Unidade.objects.get(codigo_eol=eol_dre)
            qs = Associacao.objects.filter(unidade__dre=dre)
        else:
            qs = Associacao.objects.all()

        log_execucao = ''
        for associacao in qs:
            migrar_associacao_vacancia(associacao)
            log_execucao += f"{associacao.unidade.codigo_eol} - {associacao.nome}\n"

        solicitacao.status_processamento = StatusProcessamento.SUCESSO
        solicitacao.log_execucao = (
            "Migração(ões) de Vacância efetuada(s) com sucesso: "
            f"\n{log_execucao}\nTotal: {qs.count()} de Associação(ões)"
        )
        solicitacao.save()
    except Exception as err:
        solicitacao.status_processamento = StatusProcessamento.ERRO
        solicitacao.log_execucao = f"Falha na Migração de Vacância: \n{err}"
        solicitacao.save()
