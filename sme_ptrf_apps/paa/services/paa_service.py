import logging
from datetime import date
from decimal import Decimal

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Sum
from django.db import transaction

from weasyprint import HTML, CSS

from sme_ptrf_apps.paa.models import (
    ParametroPaa,
    ProgramaPdde,
    PrioridadePaa,
    ReceitaPrevistaPaa,
    ReceitaPrevistaPdde,
    RecursoProprioPaa,
)
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum

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
    def gerar_arquivo_pdf_previa_paa(cls, paa, dados):
        logger.info('Iniciando task gerar_pdf_previa_paa')

        prioridades = cls._prioridades_por_recurso(paa)
        plano_orcamentario = cls._plano_orcamentario(paa)
        atividades_previstas = cls._atividades_previstas(paa)
        conclusao = cls._conclusao_paa(paa)

        html_template = get_template('pdf/paa/pdf_previa_paa.html')
        rendered_html = html_template.render({
            'dados': dados,
            'paa': paa,
            'objetivos': paa.objetivos.all(),
            'atividades': paa.atividadeestatutariapaa_set.select_related('atividade_estatutaria'),
            'prioridades': prioridades,
            'plano_orcamentario': plano_orcamentario,
            'atividades_previstas': atividades_previstas,
            'conclusao_paa': conclusao,
            'base_static_url': staticfiles_storage.location
        })

        pdf_file = HTML(
            string=rendered_html,
            base_url=staticfiles_storage.location
        ).write_pdf(
            stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-previa-paa.css')]
        )

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="previa_plano_anual_atividades.pdf"'

        return response

    @classmethod
    def _prioridades_por_recurso(cls, paa):
        prioridades_qs = paa.prioridadepaa_set.filter(prioridade=True).select_related(
            'acao_associacao__acao',
            'programa_pdde',
            'acao_pdde',
            'tipo_despesa_custeio',
            'especificacao_material'
        )

        def _label_recurso(prioridade):
            if prioridade.recurso == RecursoOpcoesEnum.PTRF.name:
                if prioridade.acao_associacao and prioridade.acao_associacao.acao:
                    return prioridade.acao_associacao.acao.nome
                return RecursoOpcoesEnum.PTRF.value
            if prioridade.recurso == RecursoOpcoesEnum.PDDE.name:
                if prioridade.acao_pdde:
                    return prioridade.acao_pdde.nome
                if prioridade.programa_pdde:
                    return prioridade.programa_pdde.nome
                return RecursoOpcoesEnum.PDDE.value
            return RecursoOpcoesEnum.RECURSO_PROPRIO.value

        def _label_tipo_aplicacao(prioridade):
            if prioridade.tipo_aplicacao:
                try:
                    return TipoAplicacaoOpcoesEnum[prioridade.tipo_aplicacao].value
                except KeyError:
                    return prioridade.tipo_aplicacao
            return ""

        def _label_tipo_despesa(prioridade):
            if prioridade.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                return "Aquisição de material permanente"
            if prioridade.tipo_despesa_custeio:
                return prioridade.tipo_despesa_custeio.nome
            return "Aquisição de material de consumo"

        def _especificacao(prioridade):
            if prioridade.especificacao_material:
                return prioridade.especificacao_material.descricao
            return ""

        prioridades_ptrf = []
        prioridades_pdde = []
        prioridades_outros = []

        for prioridade in prioridades_qs:
            item = {
                'recurso': _label_recurso(prioridade),
                'tipo_aplicacao': _label_tipo_aplicacao(prioridade),
                'tipo_despesa': _label_tipo_despesa(prioridade),
                'especificacao': _especificacao(prioridade),
                'valor_total': prioridade.valor_total or Decimal("0.00")
            }

            if prioridade.recurso == RecursoOpcoesEnum.PTRF.name:
                prioridades_ptrf.append(item)
            elif prioridade.recurso == RecursoOpcoesEnum.PDDE.name:
                prioridades_pdde.append(item)
            else:
                prioridades_outros.append(item)

        return {
            'ptrf': prioridades_ptrf,
            'pdde': prioridades_pdde,
            'outros': prioridades_outros,
            'total_ptrf': sum([p['valor_total'] for p in prioridades_ptrf], Decimal("0.00")),
            'total_pdde': sum([p['valor_total'] for p in prioridades_pdde], Decimal("0.00")),
            'total_outros': sum([p['valor_total'] for p in prioridades_outros], Decimal("0.00")),
        }

    @classmethod
    def _plano_orcamentario(cls, paa):
        def default_bloco():
            return {
                'linhas': [],
                'totais': {'receita': Decimal('0.00'), 'despesa': Decimal('0.00'), 'saldo': Decimal('0.00')}
            }

        def adiciona_totais(bloco, linha):
            bloco['totais']['receita'] += linha['receita_total']
            bloco['totais']['despesa'] += linha['despesa_total']
            bloco['totais']['saldo'] += linha['saldo_total']

        def calcula_linha(recurso_nome, receita, despesa):
            saldo = {
                'custeio': receita['custeio'] - despesa['custeio'],
                'capital': receita['capital'] - despesa['capital'],
                'livre': receita['livre'] - despesa['livre'],
            }
            return {
                'recurso': recurso_nome,
                'receita': receita,
                'despesa': despesa,
                'saldo': saldo,
                'receita_total': sum(receita.values()),
                'despesa_total': sum(despesa.values()),
                'saldo_total': sum(saldo.values()),
            }

        # PTRF
        ptrf = default_bloco()
        receitas_ptrf = {}
        for rec in ReceitaPrevistaPaa.objects.filter(paa=paa).select_related('acao_associacao__acao'):
            nome_recurso = rec.acao_associacao.acao.nome if rec.acao_associacao and rec.acao_associacao.acao else "PTRF"
            data = receitas_ptrf.setdefault(nome_recurso, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            data['custeio'] += Decimal(rec.saldo_congelado_custeio or 0) + Decimal(rec.previsao_valor_custeio or 0)
            data['capital'] += Decimal(rec.saldo_congelado_capital or 0) + Decimal(rec.previsao_valor_capital or 0)
            data['livre'] += Decimal(rec.saldo_congelado_livre or 0) + Decimal(rec.previsao_valor_livre or 0)

        despesas_ptrf = {}
        for prio in PrioridadePaa.objects.filter(paa=paa, recurso=RecursoOpcoesEnum.PTRF.name, prioridade=True).select_related('acao_associacao__acao'):
            nome_recurso = prio.acao_associacao.acao.nome if prio.acao_associacao and prio.acao_associacao.acao else "PTRF"
            data = despesas_ptrf.setdefault(nome_recurso, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            valor = Decimal(prio.valor_total or 0)
            if prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                data['capital'] += valor
            elif prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                data['custeio'] += valor
            else:
                data['livre'] += valor

        recursos_ptrf = set(list(receitas_ptrf.keys()) + list(despesas_ptrf.keys()))
        for nome in sorted(recursos_ptrf):
            receita = receitas_ptrf.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            despesa = despesas_ptrf.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            linha = calcula_linha(nome, receita, despesa)
            ptrf['linhas'].append(linha)
            adiciona_totais(ptrf, linha)

        # PDDE
        pdde = default_bloco()
        receitas_pdde = {}
        for rec in ReceitaPrevistaPdde.objects.filter(paa=paa).select_related('acao_pdde'):
            nome_recurso = rec.acao_pdde.nome if rec.acao_pdde else "PDDE"
            data = receitas_pdde.setdefault(nome_recurso, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            data['custeio'] += Decimal(rec.saldo_custeio or 0) + Decimal(rec.previsao_valor_custeio or 0)
            data['capital'] += Decimal(rec.saldo_capital or 0) + Decimal(rec.previsao_valor_capital or 0)
            data['livre'] += Decimal(rec.saldo_livre or 0) + Decimal(rec.previsao_valor_livre or 0)

        despesas_pdde = {}
        for prio in PrioridadePaa.objects.filter(paa=paa, recurso=RecursoOpcoesEnum.PDDE.name, prioridade=True).select_related('acao_pdde', 'programa_pdde'):
            nome_recurso = prio.acao_pdde.nome if prio.acao_pdde else (prio.programa_pdde.nome if prio.programa_pdde else "PDDE")
            data = despesas_pdde.setdefault(nome_recurso, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            valor = Decimal(prio.valor_total or 0)
            if prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                data['capital'] += valor
            elif prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                data['custeio'] += valor
            else:
                data['livre'] += valor

        recursos_pdde = set(list(receitas_pdde.keys()) + list(despesas_pdde.keys()))
        for nome in sorted(recursos_pdde):
            receita = receitas_pdde.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            despesa = despesas_pdde.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            linha = calcula_linha(nome, receita, despesa)
            pdde['linhas'].append(linha)
            adiciona_totais(pdde, linha)

        # Recursos próprios
        recursos_proprios = default_bloco()
        receitas_outros = {}
        receita_total_outros = RecursoProprioPaa.objects.filter(paa=paa).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        if receita_total_outros:
            receitas_outros['Recursos próprios'] = {
                'custeio': Decimal('0.00'),
                'capital': Decimal('0.00'),
                'livre': Decimal(receita_total_outros)
            }

        despesas_outros = {}
        for prio in PrioridadePaa.objects.filter(paa=paa, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, prioridade=True):
            nome_recurso = "Recursos próprios"
            data = despesas_outros.setdefault(nome_recurso, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            valor = Decimal(prio.valor_total or 0)
            if prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                data['capital'] += valor
            elif prio.tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                data['custeio'] += valor
            else:
                data['livre'] += valor

        recursos_outros = set(list(receitas_outros.keys()) + list(despesas_outros.keys()))
        for nome in sorted(recursos_outros):
            receita = receitas_outros.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            despesa = despesas_outros.get(nome, {'custeio': Decimal('0.00'), 'capital': Decimal('0.00'), 'livre': Decimal('0.00')})
            linha = calcula_linha(nome, receita, despesa)
            recursos_proprios['linhas'].append(linha)
            adiciona_totais(recursos_proprios, linha)

        return {
            'ptrf': ptrf,
            'pdde': pdde,
            'outros': recursos_proprios
        }

    @classmethod
    def _atividades_previstas(cls, paa):
        meses_pt = [
            "",
            "JANEIRO", "FEVEREIRO", "MARCO", "ABRIL", "MAIO", "JUNHO",
            "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
        ]

        estatutarias = []
        for atividade_paa in paa.atividadeestatutariapaa_set.select_related('atividade_estatutaria').all():
            atividade = atividade_paa.atividade_estatutaria
            data = atividade_paa.data
            mes_ano = ""
            if data:
                mes_ano = f"{meses_pt[data.month]}/{data.year}"
            estatutarias.append({
                'tipo': atividade.get_tipo_display() if atividade else '',
                'data': data,
                'nome': atividade.nome if atividade else '',
                'mes_ano': mes_ano
            })

        outros_recursos = []
        total_outros = Decimal('0.00')
        for recurso in RecursoProprioPaa.objects.filter(paa=paa).select_related('fonte_recurso'):
            valor = Decimal(recurso.valor or 0)
            total_outros += valor
            outros_recursos.append({
                'tipo': recurso.fonte_recurso.nome if recurso.fonte_recurso else '',
                'data': recurso.data_prevista,
                'descricao': recurso.descricao,
                'valor': valor
            })

        return {
            'estatutarias': estatutarias,
            'outros_recursos': outros_recursos,
            'total_outros': total_outros
        }

    @classmethod
    def _conclusao_paa(cls, paa):
        try:
            parametro = ParametroPaa.get()
        except Exception:
            parametro = None

        if parametro:
            if parametro.conclusao_do_paa_ue_1:
                return parametro.conclusao_do_paa_ue_1
            if parametro.conclusao_do_paa_ue_2:
                return parametro.conclusao_do_paa_ue_2

        return paa.texto_conclusao or ""

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

                    # Ref História (134829) de desativação de Ações no PAA
                    acao_associacao=prioridade.acao_associacao if (
                        prioridade.acao_associacao and
                        prioridade.acao_associacao.acao and
                        prioridade.acao_associacao.acao.exibir_paa) else None,
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
