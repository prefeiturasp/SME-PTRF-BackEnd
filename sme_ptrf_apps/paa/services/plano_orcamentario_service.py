import logging
import math
from decimal import Decimal
from django.db.models import Sum

from sme_ptrf_apps.paa.models import Paa, RecursoProprioPaa
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum

logger = logging.getLogger(__name__)

CAMPOS_ORCAMENTARIOS = ('custeio', 'capital', 'livre', 'total')


def _to_float(val, default=None):
    """
    Converte valor para float.
    Se val for None, NaN, inf ou inválido, retorna default.
    """
    if val is None:
        return default
    try:
        result = float(val)
        if math.isnan(result) or math.isinf(result):
            return default
        return result
    except (ValueError, TypeError, OverflowError):
        return default


def _converter_valores_para_float(valores_dict, campos=None):
    """
    Converte valores de um dicionário para float.
    Garante que os campos custeio, capital, livre e total existam e sejam válidos (None/NaN → 0.0).
    """
    campos = campos or CAMPOS_ORCAMENTARIOS
    return {campo: _to_float(valores_dict.get(campo), 0.0) for campo in campos}


class PlanoOrcamentarioService:
    """Service para agregar e formatar dados do Plano Orçamentário"""

    def __init__(self, paa: Paa):
        self.paa = paa

    def _calcular_saldo(self, receitas, despesas):
        """
        Calcula saldo considerando regras de negativos.
        Se custeio ou capital ficarem negativos, o déficit é deduzido do saldo de livre aplicação.
        """
        saldo_custeio_bruto = receitas['custeio'] - despesas['custeio']
        saldo_capital_bruto = receitas['capital'] - despesas['capital']
        saldo_livre_bruto = receitas['livre'] - despesas['livre']

        saldo_custeio_final = saldo_custeio_bruto if saldo_custeio_bruto >= 0 else Decimal('0')
        saldo_livre_final = saldo_livre_bruto

        if saldo_custeio_bruto < 0:
            saldo_livre_final += saldo_custeio_bruto
            saldo_custeio_final = Decimal('0')

        saldo_capital_final = saldo_capital_bruto if saldo_capital_bruto >= 0 else Decimal('0')

        if saldo_capital_bruto < 0:
            saldo_livre_final += saldo_capital_bruto
            saldo_capital_final = Decimal('0')

        return {
            'custeio': saldo_custeio_final,
            'capital': saldo_capital_final,
            'livre': saldo_livre_final,
            'total': saldo_custeio_final + saldo_capital_final + saldo_livre_final
        }

    def _obter_saldos_finais(self, receita_prevista, saldos_atual):
        """
        Obtém saldos finais verificando se estão congelados.
        Se o saldo estiver congelado e todos os valores congelados estiverem preenchidos,
        retorna os valores congelados. Caso contrário, retorna os saldos atuais.

        Args:
            receita_prevista: Dicionário com dados da receita prevista (pode conter saldos congelados)
            saldos_atual: Dicionário com saldos atuais da ação

        Returns:
            Dicionário com saldos finais (saldo_atual_custeio, saldo_atual_capital, saldo_atual_livre)
        """
        saldo_congelado_custeio = receita_prevista.get('saldo_congelado_custeio')
        saldo_congelado_capital = receita_prevista.get('saldo_congelado_capital')
        saldo_congelado_livre = receita_prevista.get('saldo_congelado_livre')

        saldo_esta_congelado = (
            self.paa.saldo_congelado_em is not None and
            saldo_congelado_custeio is not None and
            saldo_congelado_capital is not None and
            saldo_congelado_livre is not None
        )

        if saldo_esta_congelado:
            saldo_custeio_final = float(saldo_congelado_custeio)
            saldo_capital_final = float(saldo_congelado_capital)
            saldo_livre_final = float(saldo_congelado_livre)
        else:
            saldo_custeio_final = float(saldos_atual.get('saldo_atual_custeio', 0))
            saldo_capital_final = float(saldos_atual.get('saldo_atual_capital', 0))
            saldo_livre_final = float(saldos_atual.get('saldo_atual_livre', 0))

        return {
            'saldo_atual_custeio': saldo_custeio_final,
            'saldo_atual_capital': saldo_capital_final,
            'saldo_atual_livre': saldo_livre_final
        }

    def _obter_receitas_ptrf(self):
        """
        Obtém receitas PTRF formatadas com saldos atuais e congelados.
        Retorna lista de receitas com informações completas para cada ação.
        """
        acoes_associacoes = self.paa.associacao.acoes.select_related('acao').filter(
            acao__exibir_paa=True
        ).all()

        receitas = []
        for acao_assoc in acoes_associacoes:
            try:
                saldos_atual = acao_assoc.saldo_atual()
            except Exception as e:
                logger.error(f"Erro ao obter saldos para ação de associação {acao_assoc.uuid}: {str(e)}")
                saldos_atual = {}

            acao_uuid = str(acao_assoc.acao.uuid)
            receitas_previstas_objetos = self.paa.receitaprevistapaa_set.filter(
                paa=self.paa,
                acao_associacao=acao_assoc
            )

            receita_prevista_obj = receitas_previstas_objetos.first()
            if receita_prevista_obj:
                receita_prevista = {
                    'uuid': str(receita_prevista_obj.uuid),
                    'id': receita_prevista_obj.id,
                    'previsao_valor_custeio': float(receita_prevista_obj.previsao_valor_custeio or 0),
                    'previsao_valor_capital': float(receita_prevista_obj.previsao_valor_capital or 0),
                    'previsao_valor_livre': float(receita_prevista_obj.previsao_valor_livre or 0),
                    'saldo_congelado_custeio': _to_float(receita_prevista_obj.saldo_congelado_custeio),
                    'saldo_congelado_capital': _to_float(receita_prevista_obj.saldo_congelado_capital),
                    'saldo_congelado_livre': _to_float(receita_prevista_obj.saldo_congelado_livre),
                }
                receitas_previstas_data = [receita_prevista]
            else:
                receita_prevista = {}
                receitas_previstas_data = []

            saldos_finais = self._obter_saldos_finais(receita_prevista, saldos_atual)

            acao_obj = acao_assoc.acao
            acao_data = {
                'uuid': str(acao_obj.uuid),
                'id': acao_obj.id,
                'nome': acao_obj.nome,
                'e_recursos_proprios': bool(acao_obj.e_recursos_proprios or False),
                'aceita_capital': bool(acao_obj.aceita_capital or False),
                'aceita_custeio': bool(acao_obj.aceita_custeio or False),
                'aceita_livre': bool(acao_obj.aceita_livre or False),
                'exibir_paa': bool(acao_obj.exibir_paa) if acao_obj.exibir_paa is not None else True,
            }

            receitas.append({
                'uuid': acao_uuid,
                'acao': acao_data,
                'receitas_previstas_paa': receitas_previstas_data,
                'saldos': saldos_finais
            })
        return receitas

    def _obter_prioridades_agrupadas(self):
        """
        Obtém prioridades agrupadas por recurso (PTRF ou PDDE).
        Agrupa valores de custeio e capital por ação (PTRF) ou programa (PDDE).
        """
        prioridades_qs = queryset_prioridades_paa(self.paa.prioridadepaa_set.all())
        prioridades_list = list(prioridades_qs)

        prioridades_ptrf = {}
        prioridades_pdde = {}

        for prioridade in prioridades_list:
            recurso = prioridade.recurso

            if recurso == RecursoOpcoesEnum.PTRF.name:
                if not prioridade.acao_associacao:
                    continue
                acao_uuid = str(prioridade.acao_associacao.acao.uuid)
                if acao_uuid not in prioridades_ptrf:
                    prioridades_ptrf[acao_uuid] = {
                        'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')
                    }

                tipo_aplicacao = (prioridade.tipo_aplicacao or '').upper()
                valor = Decimal(str(prioridade.valor_total or 0))

                if 'CUSTEIO' in tipo_aplicacao:
                    prioridades_ptrf[acao_uuid]['custeio'] += valor
                elif 'CAPITAL' in tipo_aplicacao:
                    prioridades_ptrf[acao_uuid]['capital'] += valor

            elif recurso == RecursoOpcoesEnum.PDDE.name:
                if not prioridade.acao_pdde:
                    continue

                acao_pdde_uuid = str(prioridade.acao_pdde.uuid)
                if acao_pdde_uuid not in prioridades_pdde:
                    prioridades_pdde[acao_pdde_uuid] = {
                        'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')
                    }

                tipo_aplicacao = (prioridade.tipo_aplicacao or '').upper()
                valor = Decimal(str(prioridade.valor_total or 0))

                if 'CUSTEIO' in tipo_aplicacao:
                    prioridades_pdde[acao_pdde_uuid]['custeio'] += valor
                elif 'CAPITAL' in tipo_aplicacao:
                    prioridades_pdde[acao_pdde_uuid]['capital'] += valor

        return {
            'PTRF': prioridades_ptrf,
            'PDDE': prioridades_pdde
        }

    def _obter_acoes_pdde_totais(self):
        """
        Obtém totais por ação PDDE.
        Retorna lista de ações PDDE com valores totais de receitas.
        Apenas retorna ações que têm receitas ou prioridades para este PAA.
        """
        from sme_ptrf_apps.paa.models import AcaoPdde, ReceitaPrevistaPdde

        acoes_com_receitas = AcaoPdde.objects.filter(
            status=AcaoPdde.STATUS_ATIVA,
            receitaprevistapdde__paa=self.paa
        ).distinct()
        acoes_com_prioridades = AcaoPdde.objects.filter(
            status=AcaoPdde.STATUS_ATIVA,
            prioridadepaa__paa=self.paa
        ).distinct()
        acoes_pdde = (acoes_com_receitas | acoes_com_prioridades).distinct()
        acoes_com_totais = []

        for acao_pdde in acoes_pdde:
            receitas_previstas = ReceitaPrevistaPdde.objects.filter(
                acao_pdde=acao_pdde,
                paa=self.paa
            )

            agrega_custeio = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_custeio'),
                previsao_total=Sum('previsao_valor_custeio')
            )
            saldo_c = agrega_custeio['saldo_total'] or Decimal('0')
            previsao_c = agrega_custeio['previsao_total'] or Decimal('0')
            valores_custeio = saldo_c + previsao_c

            agrega_capital = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_capital'),
                previsao_total=Sum('previsao_valor_capital')
            )
            saldo_k = agrega_capital['saldo_total'] or Decimal('0')
            previsao_k = agrega_capital['previsao_total'] or Decimal('0')
            valores_capital = saldo_k + previsao_k

            agrega_livre = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_livre'),
                previsao_total=Sum('previsao_valor_livre')
            )
            saldo_l = agrega_livre['saldo_total'] or Decimal('0')
            previsao_l = agrega_livre['previsao_total'] or Decimal('0')
            valores_livre = saldo_l + previsao_l

            aceita_custeio = bool(acao_pdde.aceita_custeio)
            aceita_capital = bool(acao_pdde.aceita_capital)
            aceita_livre = bool(acao_pdde.aceita_livre_aplicacao)

            acoes_com_totais.append({
                'uuid': str(acao_pdde.uuid),
                'nome': acao_pdde.nome,
                'aceita_custeio': aceita_custeio,
                'aceita_capital': aceita_capital,
                'aceita_livre_aplicacao': aceita_livre,
                'total_valor_custeio': float(valores_custeio),
                'total_valor_capital': float(valores_capital),
                'total_valor_livre_aplicacao': float(valores_livre),
                'total': float(valores_custeio + valores_capital + valores_livre)
            })

        return acoes_com_totais

    def _obter_total_recursos_proprios(self):
        """
        Obtém total de recursos próprios do PAA.
        Soma todos os valores de recursos próprios vinculados ao PAA.
        """
        queryset = RecursoProprioPaa.objects.filter(
            associacao=self.paa.associacao,
            paa=self.paa
        )
        valor_total = queryset.aggregate(total=Sum('valor'))
        return valor_total.get('total') or Decimal('0')

    def _obter_receitas_outros_recursos(self):
        """
        Obtém receitas de outros recursos do período formatadas.
        Retorna lista com receitas de recursos próprios e outros recursos.
        """
        from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, ReceitaPrevistaOutroRecursoPeriodo
        from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum

        receitas = []

        total_recursos_proprios = self._obter_total_recursos_proprios()
        receitas.append({
            'uuid': RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            'nome': 'Recursos Próprios',
            'tipo': 'RECURSO_PROPRIO',
            'receitas': {
                'custeio': Decimal('0'),
                'capital': Decimal('0'),
                'livre': total_recursos_proprios,
                'total': total_recursos_proprios
            }
        })

        outros_recursos_periodo = OutroRecursoPeriodoPaa.objects.disponiveis_para_paa(self.paa)

        for outro_recurso_periodo in outros_recursos_periodo:
            receitas_previstas = ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
                paa=self.paa,
                outro_recurso_periodo=outro_recurso_periodo
            )

            agrega_custeio = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_custeio'),
                previsao_total=Sum('previsao_valor_custeio')
            )
            sc = agrega_custeio['saldo_total'] or Decimal('0')
            pc = agrega_custeio['previsao_total'] or Decimal('0')
            valores_custeio = sc + pc

            agrega_capital = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_capital'),
                previsao_total=Sum('previsao_valor_capital')
            )
            sk = agrega_capital['saldo_total'] or Decimal('0')
            pk = agrega_capital['previsao_total'] or Decimal('0')
            valores_capital = sk + pk

            agrega_livre = receitas_previstas.aggregate(
                saldo_total=Sum('saldo_livre'),
                previsao_total=Sum('previsao_valor_livre')
            )
            sl = agrega_livre['saldo_total'] or Decimal('0')
            pl = agrega_livre['previsao_total'] or Decimal('0')
            valores_livre = sl + pl

            receitas.append({
                'uuid': str(outro_recurso_periodo.outro_recurso.uuid),
                'nome': outro_recurso_periodo.outro_recurso.nome,
                'tipo': 'OUTRO_RECURSO',
                'receitas': {
                    'custeio': valores_custeio,
                    'capital': valores_capital,
                    'livre': valores_livre,
                    'total': valores_custeio + valores_capital + valores_livre
                }
            })

        return receitas

    def _obter_prioridades_outros_recursos(self):
        """
        Obtém prioridades de recursos próprios e outros recursos agrupadas.
        Retorna dicionário com prioridades agrupadas por UUID do recurso.
        """
        from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum

        prioridades_qs = self.paa.prioridadepaa_set.filter(
            recurso__in=[
                RecursoOpcoesEnum.RECURSO_PROPRIO.name,
                RecursoOpcoesEnum.OUTRO_RECURSO.name
            ]
        )

        prioridades_agrupadas = {}

        for prioridade in prioridades_qs:
            if prioridade.recurso == RecursoOpcoesEnum.RECURSO_PROPRIO.name:
                chave = RecursoOpcoesEnum.RECURSO_PROPRIO.name
            elif prioridade.recurso == RecursoOpcoesEnum.OUTRO_RECURSO.name and prioridade.outro_recurso:
                chave = str(prioridade.outro_recurso.uuid)
            else:
                continue

            if chave not in prioridades_agrupadas:
                prioridades_agrupadas[chave] = {
                    'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')
                }

            tipo_aplicacao = (prioridade.tipo_aplicacao or '').upper()
            valor = Decimal(str(prioridade.valor_total or 0))

            if 'CUSTEIO' in tipo_aplicacao:
                prioridades_agrupadas[chave]['custeio'] += valor
            elif 'CAPITAL' in tipo_aplicacao:
                prioridades_agrupadas[chave]['capital'] += valor
            elif 'LIVRE' in tipo_aplicacao:
                prioridades_agrupadas[chave]['livre'] += valor

        return prioridades_agrupadas

    def _calcular_secao_outros_recursos(self, receitas_outros_recursos, prioridades_outros_recursos):
        """
        Calcula seção de Outros Recursos do plano orçamentário.
        Cria linhas com receitas, despesas e saldos para recursos próprios e outros recursos.
        """
        if not receitas_outros_recursos:
            return None

        linhas = []
        total_receitas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}
        total_despesas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}

        for receita_item in receitas_outros_recursos:
            receita_valores = receita_item['receitas']
            recurso_uuid = receita_item['uuid']
            despesas_raw = prioridades_outros_recursos.get(recurso_uuid, {})
            despesa_custeio = Decimal(str(despesas_raw.get('custeio', 0) or 0))
            despesa_capital = Decimal(str(despesas_raw.get('capital', 0) or 0))
            despesa_livre = Decimal(str(despesas_raw.get('livre', 0) or 0))
            despesa_valores = {
                'custeio': despesa_custeio,
                'capital': despesa_capital,
                'livre': despesa_livre,
                'total': despesa_custeio + despesa_capital + despesa_livre
            }

            saldo_valores = self._calcular_saldo(receita_valores, despesa_valores)

            # Verifica se há algum valor em custeio, capital ou livre
            tem_valor_custeio = any([
                receita_valores['custeio'] != Decimal('0')
            ])
            tem_valor_capital = any([
                receita_valores['capital'] != Decimal('0')
            ])
            tem_valor_livre = any([
                receita_valores['livre'] != Decimal('0')
            ])

            # Se não houver nenhum valor na ação, não adiciona a linha
            if not (tem_valor_custeio or tem_valor_capital or tem_valor_livre):
                continue
            ocultar_custeio_capital = receita_item['tipo'] == 'RECURSO_PROPRIO'

            linhas.append({
                'key': recurso_uuid,
                'nome': receita_item['nome'],
                'exibirCusteio': tem_valor_custeio,
                'exibirCapital': tem_valor_capital,
                'exibirLivre': tem_valor_livre,
                'receitas': _converter_valores_para_float(receita_valores),
                'despesas': _converter_valores_para_float(despesa_valores),
                'saldos': _converter_valores_para_float(saldo_valores),
                'ocultarCusteioCapital': ocultar_custeio_capital
            })

            total_receitas['custeio'] += receita_valores['custeio']
            total_receitas['capital'] += receita_valores['capital']
            total_receitas['livre'] += receita_valores['livre']
            total_despesas['custeio'] += despesa_valores['custeio']
            total_despesas['capital'] += despesa_valores['capital']
            total_despesas['livre'] += despesa_valores['livre']

        if not linhas:
            return None

        total_receitas['total'] = total_receitas['custeio'] + total_receitas['capital'] + total_receitas['livre']
        total_despesas['total'] = total_despesas['custeio'] + total_despesas['capital'] + total_despesas['livre']
        total_saldos = self._calcular_saldo(total_receitas, total_despesas)
        linhas.append({
            'key': 'outros-recursos-total',
            'nome': 'TOTAL',
            'isTotal': True,
            'receitas': _converter_valores_para_float(total_receitas),
            'despesas': _converter_valores_para_float(total_despesas),
            'saldos': _converter_valores_para_float(total_saldos),
            'ocultarCusteioCapital': True
        })

        return {
            'key': 'outros_recursos',
            'titulo': 'Outros Recursos',
            'linhas': linhas
        }

    def _calcular_receita_base(self, item):
        """
        Calcula receita base de um item PTRF.
        Considera saldo (já verificado se congelado ou atual) mais valores de previsão.
        """
        receitas_previstas = item.get('receitas_previstas_paa') or []
        if receitas_previstas:
            receita_prevista = receitas_previstas[0]
        else:
            receita_prevista = {}
        saldos = item.get('saldos', {})

        saldo_custeio_base = max(0, saldos.get('saldo_atual_custeio', 0))
        saldo_capital_base = max(0, saldos.get('saldo_atual_capital', 0))
        saldo_livre_base = max(0, saldos.get('saldo_atual_livre', 0))

        previsao_custeio = Decimal(str(receita_prevista.get('previsao_valor_custeio', 0) or 0))
        previsao_capital = Decimal(str(receita_prevista.get('previsao_valor_capital', 0) or 0))
        previsao_livre = Decimal(str(receita_prevista.get('previsao_valor_livre', 0) or 0))
        saldo_custeio = Decimal(str(saldo_custeio_base or 0))
        saldo_capital = Decimal(str(saldo_capital_base or 0))
        saldo_livre = Decimal(str(saldo_livre_base or 0))

        custeio = previsao_custeio + saldo_custeio
        capital = previsao_capital + saldo_capital
        livre = previsao_livre + saldo_livre

        return {
            'custeio': custeio,
            'capital': capital,
            'livre': livre,
            'total': custeio + capital + livre
        }

    def _calcular_secao_ptrf(self, receitas_ptrf, prioridades_ptrf):
        """
        Calcula seção PTRF do plano orçamentário.
        Cria linhas com receitas, despesas e saldos para cada ação PTRF.
        """
        if not receitas_ptrf:
            return None

        linhas = []
        total_receitas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}
        total_despesas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}

        for receita in receitas_ptrf:
            receita_valores = self._calcular_receita_base(receita)
            if (receita_valores['custeio'] == Decimal('0') and
                    receita_valores['capital'] == Decimal('0') and
                    receita_valores['livre'] == Decimal('0')):
                continue

            despesas_raw = prioridades_ptrf.get(receita['uuid'], {})
            despesa_custeio = Decimal(str(despesas_raw.get('custeio', 0) or 0))
            despesa_capital = Decimal(str(despesas_raw.get('capital', 0) or 0))
            despesa_valores = {
                'custeio': despesa_custeio,
                'capital': despesa_capital,
                'livre': Decimal('0'),
                'total': despesa_custeio + despesa_capital
            }

            saldo_valores = self._calcular_saldo(receita_valores, despesa_valores)

            linhas.append({
                'key': receita['uuid'],
                'nome': receita['acao'].get('nome', '-'),
                # Para PTRF, sempre exibimos as três categorias,
                # mesmo quando todas estiverem zeradas.
                'exibirCusteio': True,
                'exibirCapital': True,
                'exibirLivre': True,
                'receitas': _converter_valores_para_float(receita_valores),
                'despesas': _converter_valores_para_float(despesa_valores),
                'saldos': _converter_valores_para_float(saldo_valores)
            })

            total_receitas['custeio'] += receita_valores['custeio']
            total_receitas['capital'] += receita_valores['capital']
            total_receitas['livre'] += receita_valores['livre']
            total_despesas['custeio'] += despesa_valores['custeio']
            total_despesas['capital'] += despesa_valores['capital']

        # Se nenhuma ação tiver valores, não cria seção PTRF
        if not linhas:
            return None

        total_receitas['total'] = total_receitas['custeio'] + total_receitas['capital'] + total_receitas['livre']
        total_despesas['total'] = total_despesas['custeio'] + total_despesas['capital'] + total_despesas['livre']
        total_saldos = self._calcular_saldo(total_receitas, total_despesas)
        linhas.append({
            'key': 'ptrf-total',
            'nome': 'TOTAL',
            'isTotal': True,
            'receitas': _converter_valores_para_float(total_receitas),
            'despesas': _converter_valores_para_float(total_despesas),
            'saldos': _converter_valores_para_float(total_saldos)
        })

        return {
            'key': 'ptrf',
            'titulo': 'PTRF',
            'linhas': linhas
        }

    def _calcular_secao_pdde(self, acoes_pdde, prioridades_pdde):
        """
        Calcula seção PDDE do plano orçamentário.
        Cria linhas com receitas, despesas e saldos para cada ação PDDE.
        """
        if not acoes_pdde:
            return None

        linhas = []
        total_receitas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}
        total_despesas = {'custeio': Decimal('0'), 'capital': Decimal('0'), 'livre': Decimal('0')}

        for acao in acoes_pdde:
            aceita_custeio = bool(acao.get('aceita_custeio', False))
            aceita_capital = bool(acao.get('aceita_capital', False))
            aceita_livre = bool(acao.get('aceita_livre_aplicacao', False))

            # Valores brutos de receita
            receita_custeio = Decimal(str(acao.get('total_valor_custeio', 0) or 0))
            receita_capital = Decimal(str(acao.get('total_valor_capital', 0) or 0))
            receita_livre = Decimal(str(acao.get('total_valor_livre_aplicacao', 0) or 0))

            # Desconsiderar categorias que a ação não aceita (zerar para cálculo e exibição)
            if not aceita_custeio:
                receita_custeio = Decimal('0')
            if not aceita_capital:
                receita_capital = Decimal('0')
            if not aceita_livre:
                receita_livre = Decimal('0')

            receita_valores = {
                'custeio': receita_custeio,
                'capital': receita_capital,
                'livre': receita_livre,
                'total': receita_custeio + receita_capital + receita_livre
            }

            acao_uuid = acao.get('uuid')
            despesas_raw = prioridades_pdde.get(acao_uuid, {})
            despesa_custeio = Decimal(str(despesas_raw.get('custeio', 0) or 0))
            despesa_capital = Decimal(str(despesas_raw.get('capital', 0) or 0))
            if not aceita_custeio:
                despesa_custeio = Decimal('0')
            if not aceita_capital:
                despesa_capital = Decimal('0')
            despesa_valores = {
                'custeio': despesa_custeio,
                'capital': despesa_capital,
                'livre': Decimal('0'),
                'total': despesa_custeio + despesa_capital
            }

            saldo_valores = self._calcular_saldo(receita_valores, despesa_valores)

            # Exibir linha de categoria só se a ação aceita E tem valor (receita, despesa ou saldo)
            tem_valor_custeio = (
                aceita_custeio and
                (receita_valores['custeio'] != Decimal('0') or
                 despesa_valores['custeio'] != Decimal('0') or
                 saldo_valores['custeio'] != Decimal('0'))
            )
            tem_valor_capital = (
                aceita_capital and
                (receita_valores['capital'] != Decimal('0') or
                 despesa_valores['capital'] != Decimal('0') or
                 saldo_valores['capital'] != Decimal('0'))
            )
            tem_valor_livre = (
                aceita_livre and
                (receita_valores['livre'] != Decimal('0') or
                 despesa_valores['livre'] != Decimal('0') or
                 saldo_valores['livre'] != Decimal('0'))
            )

            # Se não houver nenhuma categoria aceita com valor, não adiciona a linha da ação
            if not (tem_valor_custeio or tem_valor_capital or tem_valor_livre):
                continue

            linhas.append({
                'key': acao_uuid or acao.get('nome', ''),
                'nome': acao.get('nome', '-'),
                'exibirCusteio': tem_valor_custeio,
                'exibirCapital': tem_valor_capital,
                'exibirLivre': tem_valor_livre,
                'receitas': _converter_valores_para_float(receita_valores),
                'despesas': _converter_valores_para_float(despesa_valores),
                'saldos': _converter_valores_para_float(saldo_valores)
            })

            total_receitas['custeio'] += receita_valores['custeio']
            total_receitas['capital'] += receita_valores['capital']
            total_receitas['livre'] += receita_valores['livre']
            total_despesas['custeio'] += despesa_valores['custeio']
            total_despesas['capital'] += despesa_valores['capital']

        if not linhas:
            return None

        total_receitas['total'] = total_receitas['custeio'] + total_receitas['capital'] + total_receitas['livre']
        total_despesas['total'] = total_despesas['custeio'] + total_despesas['capital'] + total_despesas['livre']
        total_saldos = self._calcular_saldo(total_receitas, total_despesas)
        linhas.append({
            'key': 'pdde-total',
            'nome': 'TOTAL',
            'isTotal': True,
            'receitas': _converter_valores_para_float(total_receitas),
            'despesas': _converter_valores_para_float(total_despesas),
            'saldos': _converter_valores_para_float(total_saldos)
        })

        return {
            'key': 'pdde',
            'titulo': 'PDDE',
            'linhas': linhas
        }

    def construir_plano_orcamentario(self):
        """
        Constrói o plano orçamentário completo.
        """
        secoes = []

        # Prioridades PTRF, PDDE e Outros Recursos
        prioridades_agrupadas = self._obter_prioridades_agrupadas()
        prioridades_outros_recursos = self._obter_prioridades_outros_recursos()

        # Seção PTRF
        receitas_ptrf = self._obter_receitas_ptrf()
        secao_ptrf = self._calcular_secao_ptrf(receitas_ptrf, prioridades_agrupadas['PTRF'])
        if secao_ptrf:
            secoes.append(secao_ptrf)

        # Seção PDDE
        acoes_pdde = self._obter_acoes_pdde_totais()
        secao_pdde = self._calcular_secao_pdde(acoes_pdde, prioridades_agrupadas['PDDE'])
        if secao_pdde:
            secoes.append(secao_pdde)

        # Seção Outros Recursos
        receitas_outros_recursos = self._obter_receitas_outros_recursos()
        secao_outros_recursos = self._calcular_secao_outros_recursos(
            receitas_outros_recursos, prioridades_outros_recursos
        )
        if secao_outros_recursos:
            secoes.append(secao_outros_recursos)

        return {
            'secoes': secoes
        }
