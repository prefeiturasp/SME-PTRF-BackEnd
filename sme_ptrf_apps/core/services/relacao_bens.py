import logging
from waffle import get_waffle_flag_model
from django.db.models import Max, QuerySet, Count, Min, Q
from sme_ptrf_apps.core.models import RelacaoBens, Periodo, ContaAssociacao
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from ..services.relacao_bens_dados_service import (
    gerar_dados_relacao_de_bens,
    persistir_dados_relacao_bens,
    formatar_e_retornar_dados_relatorio_relacao_bens,
)
from ..services.relacao_bens_pdf_service import gerar_arquivo_relacao_de_bens_pdf

LOGGER = logging.getLogger(__name__)


class RelacaoBensService:

    def __init__(self, periodo: Periodo, conta_associacao: ContaAssociacao):
        self.periodo = periodo
        self.conta_associacao = conta_associacao

        # feature flag situação patrimonial
        self.flag_ativa = get_waffle_flag_model().objects.filter(
            name='situacao-patrimonial', everyone=True).exists()

        
    def possui_relacao_bens_no_periodo(
        self,
    ) -> tuple[bool, QuerySet[RateioDespesa], QuerySet[BemProduzido]]:
        """
        Verifica se existem bens de capital adquiridos ou produzidos
        no período informado para a conta da associação.    

        Para bens adquiridos: considera os rateios de despesas de capital
        retornados para a conta da associação no período.

        Para bens produzidos:
            - Buscaa bens produzidos com status completo cuja maior data de transação entre todas as despesas 
            esteja dentro do período informado.
            - Para cada bem, verifica as contas associadas aos seus rateios.
                - Se todos os rateios pertencerem à mesma conta, restringe os rateios à conta consultada.
                - Se houver rateios de contas diferentes, não aplica o filtro por conta: 
                o bem deve trazer todos os rateios.

        Returns:
            tuple[bool, QuerySet[RateioDespesa], QuerySet[BemProduzido]]:
                - Indicador da existência de bens de capital no período.
                - QuerySet dos rateios de despesas de capital.
                - QuerySet dos bens produzidos que atendem aos critérios.
        """

        rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
            conta_associacao=self.conta_associacao,
            periodo=self.periodo,
            aplicacao_recurso=APLICACAO_CAPITAL,
            nao_exibir_em_rel_bens=False,
        )
        
        """ Se flag desativada, considera apenas os rateios """
        if not self.flag_ativa:
            return rateios.exists(), rateios, BemProduzido.objects.none()

        bens_produzidos = (
            BemProduzido.objects.filter(
                status=BemProduzido.STATUS_COMPLETO,
            )
            .annotate(
                maior_data_transacao=Max(
                    'despesas__despesa__data_transacao',
                ),
            )
            .filter(
                maior_data_transacao__range=(
                    self.periodo.data_inicio_realizacao_despesas,
                    self.periodo.data_fim_realizacao_despesas,
                ),
            )
            .annotate(
                quantidade_contas=Count(
                    'despesas__rateios__rateio__conta_associacao_id',
                    distinct=True,
                ),
                conta_id_unica=Min(
                    'despesas__rateios__rateio__conta_associacao_id',
                ),
            )
            .filter(
                Q(quantidade_contas__gt=1)
                | Q(
                    quantidade_contas=1,
                    conta_id_unica=self.conta_associacao.id,
                ),
            )
            .prefetch_related(
                'items',
                'despesas',
                'despesas__rateios__rateio',
            )
            .distinct()
        )

        possui_bens = rateios.exists() or bens_produzidos.exists()

        return possui_bens, rateios, bens_produzidos



def gerar_arquivo_relacao_de_bens_dados_persistidos(relacao_bens, recurso_nome, recurso_nome_exibicao):
    relatorio_persistido = relacao_bens.relatoriorelacaobens_set.last()
    if relatorio_persistido:
        gerar_arquivo_relacao_de_bens_pdf(
            dados_relacao_de_bens=formatar_e_retornar_dados_relatorio_relacao_bens(
                relatorio_persistido,
                recurso_nome,
                recurso_nome_exibicao,
            ),
            relacao_bens=relacao_bens
        )


def gerar_arquivo_relacao_de_bens(periodo, conta_associacao, usuario, prestacao=None, previa=False, criar_arquivos=True):
    rel_bens_service = RelacaoBensService(periodo, conta_associacao)
    possui_bens, rateios, bens_produzidos = rel_bens_service.possui_relacao_bens_no_periodo()


    if possui_bens:
        relacao_bens, _ = RelacaoBens.objects.update_or_create(
            conta_associacao=conta_associacao,
            prestacao_conta=prestacao,
            periodo_previa=None if prestacao else periodo,
            versao=RelacaoBens.VERSAO_PREVIA if previa else RelacaoBens.VERSAO_FINAL,
            status=RelacaoBens.STATUS_EM_PROCESSAMENTO,
        )

        # PDF
        dados_relacao_de_bens = gerar_dados_relacao_de_bens(
            conta_associacao=conta_associacao,
            periodo=periodo,
            rateios=rateios,
            bens_produzidos=bens_produzidos,
            usuario=usuario,
            previa=previa
        )

        if criar_arquivos:
            # gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens=formatar_e_retornar_dados_relatorio_relacao_bens(relatorio_persistido), relacao_bens=relacao_bens)
            gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens=dados_relacao_de_bens, relacao_bens=relacao_bens)

        relacao_bens.arquivo_concluido()


def apagar_previas_relacao_de_bens(periodo, conta_associacao):
    for relacao_bens in RelacaoBens.objects.filter(periodo_previa=periodo, conta_associacao=conta_associacao):
        for relatorio in relacao_bens.relatoriorelacaobens_set.all():
            for item_relatorio in relatorio.bens.all():
                item_relatorio.delete()
            relatorio.delete()
        relacao_bens.delete()


def _retornar_dados_relatorio_relacao_de_bens(relacao_bens, recurso_nome, recurso_nome_exibicao):
    relatorio_persistido = relacao_bens.relatoriorelacaobens_set.last()
    if relatorio_persistido:
        return formatar_e_retornar_dados_relatorio_relacao_bens(
            relatorio_persistido,
            recurso_nome,
            recurso_nome_exibicao
        )
    return None


def _persistir_arquivo_relacao_de_bens(periodo, conta_associacao, usuario, prestacao=None, previa=False):    

    rel_bens_service = RelacaoBensService(periodo, conta_associacao)
    possui_bens, rateios, bens_produzidos = rel_bens_service.possui_relacao_bens_no_periodo()

    if possui_bens:
        relacao_bens, _ = RelacaoBens.objects.update_or_create(
            conta_associacao=conta_associacao,
            prestacao_conta=prestacao,
            periodo_previa=None if prestacao else periodo,
            versao=RelacaoBens.VERSAO_PREVIA if previa else RelacaoBens.VERSAO_FINAL,
            status=RelacaoBens.STATUS_A_PROCESSAR,
        ) 
        LOGGER.info(f'Relacão de bens criada/atualizada com sucesso {relacao_bens}.')

        LOGGER.info(f'Iniciando persistir_dados_relacao_bens {relacao_bens}.')

        persistir_dados_relacao_bens(
            conta_associacao=conta_associacao,
            periodo=periodo,
            rateios=rateios,
            bens_produzidos=bens_produzidos,
            relacao_bens=relacao_bens,
            usuario=usuario
        )

        return relacao_bens
    else:
        LOGGER.info("Não houve bem adquirido ou produzido no referido período (%s).", str(periodo))
    return None


def previa_relacao_de_bens_bloqueada(conta_associacao: ContaAssociacao, periodo: Periodo) -> bool:
    """
    Verifica se a geração da prévia da relação de bens está bloqueada.
    A prévia não pode ser gerada quando já existe uma versão final
    da relação de bens vinculada a uma prestação de contas da mesma
    associação e período.

    Args:
    conta_associacao: Conta de associação para a qual a prévia
        será gerada.
    periodo: Período de referência da prévia.

    Returns:
        bool: True se já existe uma versão final e a geração da prévia
        deve ser bloqueada; False caso contrário.
    """
    return RelacaoBens.objects.filter(
        prestacao_conta__associacao=conta_associacao.associacao,
        prestacao_conta__periodo=periodo,
        versao=RelacaoBens.VERSAO_FINAL,
    ).exists()
