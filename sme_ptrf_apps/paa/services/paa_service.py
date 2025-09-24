import logging
from datetime import date

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Sum
from django.db import transaction

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.models import ParametroPaa, ProgramaPdde, PrioridadePaa

logger = logging.getLogger(__name__)


class ImportacaoConfirmacaoNecessaria(Exception):
    """ Exceção de importação de quando já existem prioridades importadas e
    necessita de confirmação do usuário para remover-las e realizar a importação novamente."""

    def __init__(self, payload):
        super().__init__(payload)
        self.payload = payload


class PaaService:

    @classmethod
    def pode_elaborar_novo_paa(cls):

        mes_atual = date.today().month
        param_paa = ParametroPaa.get()
        assert param_paa.mes_elaboracao_paa is not None, ("Nenhum parâmetro de mês para Elaboração de "
                                                          "Novo PAA foi definido no Admin.")
        assert mes_atual >= param_paa.mes_elaboracao_paa, "Mês não liberado para Elaboração de novo PAA."

    @classmethod
    def gerar_arquivo_pdf_levantamento_prioridades_paa(cls, dados):
        logger.info('Iniciando task gerar_pdf_levantamento_prioridades_paa')

        html_template = get_template('pdf/paa/pdf_levantamento_prioridades_paa.html')
        rendered_html = html_template.render({'dados': dados, 'base_static_url': staticfiles_storage.location})

        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-levantamento-prioridades-paa.css')]
        )

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="paa_levantamento_prioridades.pdf"'

        return response

    @classmethod
    def somatorio_totais_por_programa_pdde(cls, paa_uuid, page_size=1000):
        # Obtem todos os programas com paginação
        qs_programas = ProgramaPdde.objects.prefetch_related('acaopdde_set').all()[:page_size]
        programas = []
        for qs_programa in qs_programas:
            # Objeto padrão por programa
            programa = {
                "uuid": str(qs_programa.uuid),
                "nome": qs_programa.nome,
                "total_valor_custeio": 0,
                "total_valor_capital": 0,
                "total_valor_livre_aplicacao": 0,
                "total": 0
            }

            # Obtem todas as ações do programa
            qs_acoes_pdde = qs_programa.acaopdde_set.all()
            for qs_acao_pdde in qs_acoes_pdde:
                # Obtem todas as receitas previstas do Programa PDDE x Ação PDDE x  PAA
                qs_receitas_previstas_pdde = qs_acao_pdde.receitaprevistapdde_set.filter(paa__uuid=paa_uuid)

                # Somar somente custeios
                valores_custeio = qs_receitas_previstas_pdde.aggregate(
                    total=Sum('saldo_custeio') + Sum('previsao_valor_custeio')
                )['total'] or 0
                programa['total_valor_custeio'] += valores_custeio

                # Somar somente capital
                valores_capital = qs_receitas_previstas_pdde.aggregate(
                    total=Sum('saldo_capital') + Sum('previsao_valor_capital')
                )['total'] or 0
                programa['total_valor_capital'] += valores_capital

                # Somar somente Livre aplicação
                valores_livre = qs_receitas_previstas_pdde.aggregate(
                    total=Sum('saldo_livre') + Sum('previsao_valor_livre')
                )['total'] or 0
                programa['total_valor_livre_aplicacao'] += valores_livre

                # Obter o valor total de cada Somatório anterior
                programa['total'] = sum([
                    programa['total_valor_custeio'],
                    programa['total_valor_capital'],
                    programa['total_valor_livre_aplicacao']
                ])

            # Adiciona o programa na lista para serialização
            programas.append(programa)

        totais = {}

        # Somente totais de custeio entre todos os programas
        totais["total_valor_custeio"] = sum([p['total_valor_custeio'] for p in programas])

        # Somente totais de capital entre todos os programas
        totais["total_valor_capital"] = sum([p['total_valor_capital'] for p in programas])

        # Somente totais de livre aplicação entre todos os programas
        totais["total_valor_livre_aplicacao"] = sum([p['total_valor_livre_aplicacao'] for p in programas])

        # total geral de todos os totais anteriores
        totais["total"] = sum([
            totais["total_valor_custeio"],
            totais["total_valor_capital"],
            totais["total_valor_livre_aplicacao"]
        ])

        objeto = {
            "programas": programas,
            "total": totais
        }
        return objeto

    @classmethod
    def importar_prioridades_paa_anterior(cls, paa_atual, paa_anterior, confirmar_importacao=False) -> list:
        prioridades_a_importar = paa_anterior.prioridadepaa_set.filter(prioridade=True)

        if not prioridades_a_importar.exists():
            raise Exception("Nenhuma prioridade encontrada para importação.")

        # Obtem prioridades (somente as importadas) do PAA atual
        prioridades_importadas_do_paa_atual = paa_atual.prioridadepaa_set.filter(paa_importado__isnull=False)

        # valida quando prioridades do PAA atual já foram importadas
        existe_prioridade_importada_no_paa_atual = prioridades_importadas_do_paa_atual.filter(
            paa_importado=paa_anterior).exists()
        if existe_prioridade_importada_no_paa_atual:
            raise Exception("Não é permitido importar novamente o mesmo PAA.")

        # Valida quando já exitem prioridades importadas no PAA atual e usuário não confirmou
        ja_existe_prioridades_importadas = prioridades_importadas_do_paa_atual.exists()

        # validação assegura que não existe prioridades importadas para notificar ao usuário
        # e validação assegura que há prioridades importadas e o usuário confirmou a importação (no aviso de front)
        if ja_existe_prioridades_importadas and not confirmar_importacao:
            raise ImportacaoConfirmacaoNecessaria((
                "Foi realizada a importação de um PAA anteriormente e todas as prioridades deste PAA anterior "
                "serão excluídas e será realizada a importação do PAA indicado."
            ))

        # Sempre remove todas as prioridades do PAA atual que são importadas
        prioridades_importadas_do_paa_atual.delete()

        with transaction.atomic():
            novas_prioridades = [
                PrioridadePaa(
                    paa=paa_atual,  # replica nova prioridade para o PAA atual
                    paa_importado=paa_anterior,  # relaciona ao PAA de importação
                    prioridade=prioridade.prioridade,
                    recurso=prioridade.recurso,
                    acao_associacao=prioridade.acao_associacao,
                    programa_pdde=prioridade.programa_pdde,
                    acao_pdde=prioridade.acao_pdde,
                    tipo_aplicacao=prioridade.tipo_aplicacao,
                    tipo_despesa_custeio=prioridade.tipo_despesa_custeio,
                    especificacao_material=prioridade.especificacao_material,
                    valor_total=None  # Redefine o valor para ser informado no front
                )
                for prioridade in prioridades_a_importar
            ]

            importados = PrioridadePaa.objects.bulk_create(novas_prioridades)
            return importados
