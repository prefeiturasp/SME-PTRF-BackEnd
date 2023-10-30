import logging
from celery import shared_task

from sme_ptrf_apps.core.models import Unidade, Associacao, MembroAssociacao
from sme_ptrf_apps.mandatos.models import SolicitacaoDeMigracao, CargoComposicao, OcupanteCargo, StatusProcessamento
from sme_ptrf_apps.mandatos.services import ServicoMandatoVigente, ServicoComposicaoVigente, \
    ServicoCriaComposicaoVigenteDoMandato

logger = logging.getLogger(__name__)


def get_mandato_vigente():
    servico_mandato_vigente = ServicoMandatoVigente()
    mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

    return mandato_vigente


def get_composicao_vigente(associacao, mandato):
    servico_composicao_vigente = ServicoComposicaoVigente(associacao=associacao, mandato=mandato)
    composicao_vigente = servico_composicao_vigente.get_composicao_vigente()

    if composicao_vigente:
        composicao_vigente.delete()

    servico_cria_composicao_vigente = ServicoCriaComposicaoVigenteDoMandato(associacao=associacao, mandato=mandato)
    composicao_vigente = servico_cria_composicao_vigente.cria_composicao_vigente()

    return composicao_vigente


def migrar_associacao(associacao):
    logger.info(f'Migrando a Associação: {associacao}')

    mandato_vigente = get_mandato_vigente()
    composicao_vigente = get_composicao_vigente(associacao=associacao, mandato=mandato_vigente)

    logger.info(f'Criado/recuperado composição vigente: {composicao_vigente}')

    # Apaga todos os campos da composição do Histórico de Membros
    CargoComposicao.objects.filter(composicao=composicao_vigente).delete()

    # Recupera todos os membros da associacao antigos
    membros_da_associacao = MembroAssociacao.objects.filter(associacao=associacao)

    for membro in membros_da_associacao:

        # Cria Ocupantes do Cargo Histórico de Membros
        logger.info(f'Iniciando a criação ou recuperação do Ocupante do Cargo Histórico de Membros')
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
        logger.info(f'Ocupante do Cargo Histórico de Membros criado/recuperado: {ocupante_do_cargo_historico_de_membros}')

        # Cria os Cargos Composição Histórico de Membros
        logger.info(f'Iniciando a criação do Cargo Composição Histórico de Membros')
        cargo_composicao_historico_de_membros = CargoComposicao.objects.create(
            composicao=composicao_vigente,
            ocupante_do_cargo=ocupante_do_cargo_historico_de_membros,
            cargo_associacao=membro.cargo_associacao,
            substituto=False,
            substituido=False,
            data_inicio_no_cargo=mandato_vigente.data_inicial,
            data_fim_no_cargo=mandato_vigente.data_final,
        )
        logger.info(f'Cargo Composição Histórico de Membros criado: {cargo_composicao_historico_de_membros}')

    associacao.migrada_para_historico_de_membros = True
    associacao.save()


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def solicitacao_de_migracao_async(
    solicitacao_uuid,
    eol_unidade=None,
    eol_dre=None,
):
    solicitacao = SolicitacaoDeMigracao.by_uuid(solicitacao_uuid)
    solicitacao.inicia_processamento()

    logger.info(f'Iniciando a task solicitacao_de_migracao_async para a Solicitação:  {solicitacao}')

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
            migrar_associacao(associacao)
            log_execucao += f"{associacao.unidade.codigo_eol} - {associacao.nome}\n"

        solicitacao.status_processamento = StatusProcessamento.SUCESSO
        solicitacao.log_execucao = f"Migração(ões) efetuada(s) com sucesso: \n{log_execucao}\nTotal: {qs.count()} de Associação(ões)"
        solicitacao.save()
    except Exception as err:
        solicitacao.status_processamento = StatusProcessamento.ERRO
        solicitacao.log_execucao = f"Falha na Migração: \n{err}"
        solicitacao.save()
