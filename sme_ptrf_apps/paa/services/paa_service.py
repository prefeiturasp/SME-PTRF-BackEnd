import logging
from datetime import date

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Sum

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.models import ParametroPaa, ProgramaPdde

logger = logging.getLogger(__name__)


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
    def somatorio_totais_por_programa_pdde(cls, paa_uuid):
        # Obtem todos os programas
        qs_programas = ProgramaPdde.objects.prefetch_related('acaopdde_set').all()
        programas = []
        for qs_programa in qs_programas:
            # Objeto padrão por programa
            programa = {
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
