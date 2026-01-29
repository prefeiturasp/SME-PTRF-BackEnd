from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.api.serializers.receita_prevista_paa_serializer import ReceitaPrevistaPaaSerializer
import logging
logger = logging.getLogger(__name__)


class ValidacaoSaldoIndisponivel(serializers.ValidationError):
    """ raise para Validação de Saldo Indisponível """
    pass


class ResumoPrioridadesService:
    def __init__(self, paa):
        self.paa = paa

    def calcula_saldos(self, key, receitas, despesas) -> dict:
        """
            Calcula os saldos com base nas receitas e despesas.

            Recebe um key para uso na chave do dicionário, e receitas e despesas
            que são dicionários com informações de custeio, capital e livre aplicação.

            :param key: chave para uso na chave do dicionário
            :param receitas: dicionário com valores de custeio, capital e livre aplicação de receitas
            :param despesas: dicionário com valores de custeio, capital e livre aplicação de despesas
            :return: dicionário com os valores de saldo de custeio, capital e livre aplicação calculados na estrutura
            adequada para uso em tabela com expand em 3 níveis
        """
        # O valor total de custeio não deve exibir o saldo negativo (considerando que a diferença seja
        #  utilizada em livre aplicação)
        total_custeio = receitas['custeio'] - despesas['custeio']
        total_custeio = total_custeio if total_custeio > 0 else 0

        # O valor total de capital não deve exibir o saldo negativo (considerando que a diferença seja
        #  utilizada, também, em livre aplicação)
        total_capital = receitas['capital'] - despesas['capital']
        total_capital = total_capital if total_capital > 0 else 0

        # Calcular os valores excedentes entre receitas (-) despesas = (se negativo) descontar de livre aplicacao
        descontar_de_livre_aplicacao = 0

        # Soma a diferença à coluna Livre Aplicação de Despesas quando não há valor suficiente de receitas para Custeio
        diferenca_custeio = receitas['custeio'] - despesas['custeio']
        # Diferença para descontar de livre aplicação (se negativo)
        descontar_de_livre_aplicacao += (diferenca_custeio * -1) if diferenca_custeio <= 0 else 0

        # Soma a diferença à coluna Livre Aplicação de Despesas quando não há valor suficiente de receitas para Capital
        diferenca_capital = receitas['capital'] - despesas['capital']
        # Diferença para descontar de livre aplicação (se negativo)
        descontar_de_livre_aplicacao += (diferenca_capital * -1) if diferenca_capital <= 0 else 0

        # Calculo do total de Livre Aplicação (valor inputado em receitas previstas (-) as diferenças calculadas acima)
        total_livre = receitas['livre_aplicacao'] - descontar_de_livre_aplicacao

        return {
            'key': key + '_' + 'saldo',
            "recurso": 'Saldo',
            "custeio": round(total_custeio, 2),
            "capital": round(total_capital, 2),
            "livre_aplicacao": round(total_livre, 2)
        }

    def calcula_node_ptrf(self) -> dict:
        from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoRetrieveSerializer

        # Queryset Somente de Prioridades do PAA do recurso PTRF
        prioridades_ptrf_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.PTRF.name)

        # Queryset de Ações de Associação do PAA ordenados por nome da Ação.
        # Ignorar Açoes com o campo exibir_paa = False (História 134829)
        acoes_associacoes_qs = self.paa.associacao.acoes.exclude(acao__exibir_paa=False).order_by('acao__nome')

        # Dados Serializados
        acoes_associacoes_data = AcaoAssociacaoRetrieveSerializer(acoes_associacoes_qs, many=True).data

        def calcula_receitas(item) -> dict:
            """
                Calcula os valores de receita de uma ação de associação do PAA.
                Retorna um Node 3 de Receita com os valores de custeio, capital e livre.
                :param item: Dado de uma ação de associação do PAA serializado
                :return: Um dicionário com a estrutura necessária para exibição em tabela de frontend com expand
                de 3 níveis de dados
            """

            def get_receita_prevista_da_acao_associacao(acao_associacao_data) -> dict:
                """
                    Retorna o índice de receitas previstas em Acao Associacao para obtenção de valores
                    de previsão ou saldo atual
                    :param acao_associacao_data: Dado de uma Acao Associacao serializado
                """
                qs_receitas_previstas_da_acao = self.paa.receitaprevistapaa_set.filter(
                    acao_associacao__acao__uuid=str(acao_associacao_data['acao']['uuid'])
                )
                # Verificar se existe retorno de receitas previstas em Acao Associacao
                receitas_previstas_paa = ReceitaPrevistaPaaSerializer(qs_receitas_previstas_da_acao, many=True).data
                receitas_previstas_paa = receitas_previstas_paa[0] if len(receitas_previstas_paa) else {}
                return receitas_previstas_paa

            def calcular_saldos_congelado_atual_previsao(congelado, atual, previsao) -> Decimal:
                """
                    Calcula o valor somado de saldo congelado, saldo atual e previsão.

                    Prioriza o valor de saldo congelado (se congelado).
                    Considera saldo atual quando não houver saldo congelado.
                    Acresce o valor previsão.

                    :param congelado: saldo congelado
                    :param atual: saldo atual
                    :param previsao: valor de previsão
                    :return: soma de (saldo congelado ou saldo atual) e previsão
                """
                previsao_valor = Decimal(previsao)
                saldo_congelado = Decimal(congelado)
                saldo_atual = Decimal(atual)

                return (saldo_congelado or saldo_atual) + previsao_valor

            def get_valor_custeio(acao_associacao_data) -> Decimal:
                """
                    Retorna o cálculo de valor de custeio em uma acao_associacao_data.
                    Procura nas receitas previstas em Acao Associacao, caso nao tenha, pega do saldo atual.
                    :param acao_associacao_data: Dado de uma Acao Associacao serializada
                    :return: Decimal com o valor de custeio
                """
                receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
                saldos = acao_associacao_data.get('saldos', {})

                previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_custeio', None) or 0)
                saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_custeio', None) or 0)
                saldo_atual = Decimal(saldos.get('saldo_atual_custeio', None) or 0)

                valor = calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

                return valor

            def get_valor_capital(acao_associacao_data) -> Decimal:
                """
                    Retorna o cálculo de valor de capital em uma acao_associacao_data.
                    Procura nas receitas previstas em Acao Associacao, caso nao tenha, pega do saldo atual.
                    :param acao_associacao_data: Dado de uma Acao Associacao
                    :return: Decimal com o valor de capital
                """
                receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
                saldos = acao_associacao_data.get('saldos', {})

                previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_capital', None) or 0)
                saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_capital', None) or 0)
                saldo_atual = Decimal(saldos.get('saldo_atual_capital', None) or 0)

                valor = calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

                return valor

            def get_valor_livre(acao_associacao_data) -> Decimal:
                """
                    Retorna o cálculo de valor de livre em uma acao_associacao_data.
                    Procura nas receitas previstas em Acao Associacao, caso nao tenha, pega do saldo atual.
                    :param acao_associacao_data: Dado de uma Acao Associacao
                    :return: Decimal com o valor de livre
                """
                receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
                saldos = acao_associacao_data.get('saldos', {})

                previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_livre', None) or 0)
                saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_livre', None) or 0)
                saldo_atual = Decimal(saldos.get('saldo_atual_livre', None) or 0)
                saldo_atual = 0 if saldo_atual < 0 else saldo_atual

                valor = calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

                return valor

            # Retorna um Node 3 de Receita
            return {
                'key': item.get('uuid') + '_' + 'receita',
                "recurso": 'Receita',
                "custeio": get_valor_custeio(item),
                "capital": get_valor_capital(item),
                "livre_aplicacao": get_valor_livre(item),
            }

        def calcula_despesas(item, receitas) -> dict:
            """
                Retorna um Node 3 de Despesas previstas (Prioridades do PAA).

                Calcula a despesa de uma ação associação baseado nas prioridades do PAA.
                A despesa considera as prioridades do PAA cadastradas com tipo CUSTEIO e CAPITAL.

                :param item: Dado de uma Acao Associacao
                :param receitas: Receitas da Acao Associacao
                :return: Node 3 de Despesa, com estrutura de um dicionário com os valores de custeio, capital e livre
                necessários para utilização em tabela no frontend com expand de 3 níveis
            """

            # Valores relacionados às "Prioridades do PAA" de uma ação associação e tipo CUSTEIO
            despesa_custeio = prioridades_ptrf_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                acao_associacao__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            # Valores relacionados às "Prioridades do PAA" de uma ação associação e tipo CAPITAL
            despesa_capital = prioridades_ptrf_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
                acao_associacao__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": 0,
            }

        # Estrutura do Node Pai para montagem de tabela de hierarquias no frontend
        # Node 1
        tipo_recurso_map = {
            'key': RecursoOpcoesEnum.PTRF.name,
            'recurso': 'PTRF Total',
            'custeio': 0,
            'capital': 0,
            'livre_aplicacao': 0,
            'children': []
        }

        # Obter a lista de Ações Associações da Associação do PAA, serializada
        for item in acoes_associacoes_data:

            # hierarquia filhos do Node Pai
            children = tipo_recurso_map['children']

            # Node 3 - Valores da Receita (Custeio, Capital, Livre)
            # Valores relacionados às "receitas previstas" de uma ação associação
            receitas = calcula_receitas(item)

            # Node 3 - Valores da Despesas (Custeio, Capital, Livre)
            despesas = calcula_despesas(item, receitas)

            # Node 3 - Valores Saldo
            saldo = self.calcula_saldos(item.get('uuid'), receitas, despesas)

            # Node 2 - Ações PTRF
            node = {
                'key': item.get('uuid'),
                # Manter nome da acao iniciando com "PTRF" (conforme protótipo do frontend)
                "recurso": ('PTRF ' + item.get('acao', {}).get('nome')).replace('PTRF PTRF', 'PTRF'),
                "custeio": saldo['custeio'],
                "capital": saldo['capital'],
                "livre_aplicacao": saldo['livre_aplicacao'],
                "parent": RecursoOpcoesEnum.PTRF.name,
                "children": []
            }

            # Adicionar o Node 2 ao Node 1
            children.append(node)

            # Adicionar os Nodes 3 ao Node 2
            node['children'].append(receitas)
            node['children'].append(despesas)
            node['children'].append(saldo)

            # Somar os valores de totais ao Node 1
            tipo_recurso_map['custeio'] += saldo['custeio']
            tipo_recurso_map['capital'] += saldo['capital']
            tipo_recurso_map['livre_aplicacao'] += saldo['livre_aplicacao']

        return tipo_recurso_map

    def calcula_node_pdde(self) -> dict:
        from sme_ptrf_apps.paa.models import AcaoPdde

        # Queryset Somente de Prioridades do PAA do recurso PDDE
        prioridades_pdde_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.PDDE.name)

        # Obtenção do Service de Programas PDDE
        acoes_PDDE = AcaoPdde.objects.all()

        def calcula_receitas(item) -> dict:
            def get_valor_capital(item) -> Decimal:
                return Decimal(item.get('total_valor_capital') or 0)

            def get_valor_custeio(item) -> Decimal:
                return Decimal(item.get('total_valor_custeio') or 0)

            def get_valor_livre(item) -> Decimal:
                """
                    Retorna o valor de livre aplicação de um item de PDDE.
                    :param item: Dado de um item de PDDE para obter o valor de livre aplicação
                    :return: Decimal com o valor de livre aplicação
                """
                return Decimal(item.get('total_valor_livre_aplicacao') or 0)

            return {
                'key': item.get('uuid') + '_' + 'receita',
                "recurso": 'Receita',
                "custeio": get_valor_custeio(item),
                "capital": get_valor_capital(item),
                "livre_aplicacao": get_valor_livre(item),
            }

        def calcula_despesas(item, receitas) -> dict:
            """
                Calcula as despesas previstas de um item de PDDE para montagem de tabela de
                hierarquias no frontend.
                :param item: Dado de um item de PDDE para compor o dict de retorno
                :param receitas: Dicionário com informações de receitas previstas de PDDE
                :return: Dicionário com a estrutura do Node 3 de "Despesas previstas".
            """

            # Valores relacionados às "Prioridades do PAA" de uma ação PDDE e tipo CUSTEIO
            despesa_custeio = prioridades_pdde_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                acao_pdde__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            # Valores relacionados às "Prioridades do PAA" de uma ação PDDE e tipo CAPITAL
            despesa_capital = prioridades_pdde_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
                acao_pdde__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": 0,
            }

        # Estrutura do Node Pai para montagem de tabela de hierarquias no frontend
        # Node 1
        tipo_recurso_map = {
            'key': RecursoOpcoesEnum.PDDE.name,
            'recurso': 'PDDE Total',
            'custeio': 0,
            'capital': 0,
            'livre_aplicacao': 0,
            'children': []
        }

        # Obter a lista de Programas da Associação do PAA, serializada
        for item in acoes_PDDE:
            # hierarquia filhos do Node Pai
            children = tipo_recurso_map['children']

            receitas_previstas_pdde = item.receitaprevistapdde_set.filter(paa__uuid=self.paa.uuid)

            acao = {
                "uuid": str(item.uuid),
                "nome": item.nome,
                "total_valor_custeio": 0,
                "total_valor_capital": 0,
                "total_valor_livre_aplicacao": 0,
            }

            # Somar somente custeios
            valores_custeio = receitas_previstas_pdde.aggregate(
                total=Sum('saldo_custeio') + Sum('previsao_valor_custeio')
            )['total'] or 0
            acao['total_valor_custeio'] += valores_custeio

            # Somar somente capital
            valores_capital = receitas_previstas_pdde.aggregate(
                total=Sum('saldo_capital') + Sum('previsao_valor_capital')
            )['total'] or 0
            acao['total_valor_capital'] += valores_capital

            # Somar somente livre aplicacao
            valores_livre = receitas_previstas_pdde.aggregate(
                total=Sum('saldo_livre') + Sum('previsao_valor_livre')
            )['total'] or 0
            acao['total_valor_livre_aplicacao'] += valores_livre

            # Node 3 - Valores da Receita (Custeio, Capital, Livre)
            # Valores relacionados aos totais do service de programa_pdde
            receitas = calcula_receitas(acao)

            # Node 3 - Valores da Despesas (Custeio, Capital, Livre)
            despesas = calcula_despesas(acao, receitas)

            # Node 3 - Valores Saldo
            saldo = self.calcula_saldos(acao.get('uuid'), receitas, despesas)

            # Node 2 - Programa PDDE
            node = {
                'key': acao.get('uuid'),
                # Manter nome da acao iniciando com "PDDE" (conforme protótipo do frontend)
                "recurso": ('PDDE ' + acao.get('nome')).replace('PDDE PDDE', 'PDDE'),
                "custeio": saldo['custeio'],
                "capital": saldo['capital'],
                "livre_aplicacao": saldo['livre_aplicacao'],
                "parent": RecursoOpcoesEnum.PDDE.name,
                "children": []
            }

            # Adicionar o Node 2 ao Node 1
            children.append(node)

            # Adicionar os Nodes 3 ao Node 2
            node['children'].append(receitas)
            node['children'].append(despesas)
            node['children'].append(saldo)

            # Somar os valores de totais ao Node 1
            tipo_recurso_map['custeio'] += saldo['custeio']
            tipo_recurso_map['capital'] += saldo['capital']
            tipo_recurso_map['livre_aplicacao'] += saldo['livre_aplicacao']

        return tipo_recurso_map

    def calcula_node_outros_recursos(self) -> dict:
        """
            Node Outros Recursos Total: (Recursos próprios + Outros Recursos)

            Recursos próprios: Item único e de posição fixa
            Outros Recursos: Lista de acordo com outros recursos habilitados para a unidade no período
        """

        from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
        from sme_ptrf_apps.paa.models.receita_prevista_outro_recurso_periodo import ReceitaPrevistaOutroRecursoPeriodo

        prioridades_recurso_proprio_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name)

        prioridades_outros_recursos_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name)

        outros_recursos_qs = OutroRecursoPeriodoPaa.objects.disponiveis_para_paa(self.paa)

        recursos_proprios_data = [
            {
                "uuid": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
                "recurso": "Recursos Próprios",
                "cor": "rgb(135, 0, 81)",
                "total_recursos_proprios": self.paa.get_total_recursos_proprios(),
                "prioridades_qs": prioridades_recurso_proprio_qs
            }
        ]

        outros_recursos_data = recursos_proprios_data + [
            {
                "uuid": f"{item.outro_recurso.uuid}",
                "recurso": item.outro_recurso.nome,
                "cor": item.outro_recurso.cor,
                "prioridades_qs": prioridades_outros_recursos_qs

            }
            for item in outros_recursos_qs
        ]

        def calcula_receitas_recursos_proprios(item) -> dict:
            return {
                'key': item.get('uuid') + '_' + 'receita',
                "recurso": 'Receita',
                "custeio": Decimal(0),
                "capital": Decimal(0),
                "livre_aplicacao": item.get("total_recursos_proprios", 0),
            }

        def calcula_receitas_outros_recursos(item, receitas_previstas_qs) -> dict:
            valor_custeio = 0
            valor_capital = 0
            valor_livre = 0

            for receita in receitas_previstas_qs:
                valor_custeio += receita.previsao_valor_custeio + receita.saldo_custeio
                valor_capital += receita.previsao_valor_capital + receita.saldo_capital
                valor_livre += receita.previsao_valor_livre + receita.saldo_livre

            return {
                'key': item.get('uuid') + '_' + 'receita',
                "recurso": 'Receita',
                "custeio": valor_custeio,
                "capital": valor_capital,
                "livre_aplicacao": valor_livre,
            }

        def calcula_despesas_recursos_proprios(item, prioridades_qs) -> dict:
            """
                Calcula as despesas previstas de um item de Recursos Próprios para montagem de tabela de
                hierarquias no frontend.
                :param item: Dado de um item de Recursos Próprios para compor o dict de retorno
                :param receitas: Dicionário com informações de despesas previstas de Recursos Próprios
                :return: Dicionário com a estrutura do Node 3 de "Despesas previstas".
            """

            despesa_custeio = prioridades_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            despesa_capital = prioridades_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": 0,
            }

        def calcula_despesas_outros_recursos(item, prioridades_qs) -> dict:
            """
                Calcula as despesas previstas de um item de Recursos Próprios para montagem de tabela de
                hierarquias no frontend.
                :param item: Dado de um item de Recursos Próprios para compor o dict de retorno
                :param receitas: Dicionário com informações de despesas previstas de Recursos Próprios
                :return: Dicionário com a estrutura do Node 3 de "Despesas previstas".
            """

            despesa_custeio = prioridades_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
                outro_recurso__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            despesa_capital = prioridades_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
                outro_recurso__uuid=item.get('uuid')
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": 0,
            }

        # Estrutura do Node Pai
        outros_recursos_total = {
            'key': RecursoOpcoesEnum.OUTRO_RECURSO.name,
            'recurso': 'Outros Recursos Total',
            'custeio': 0,
            'capital': 0,
            'livre_aplicacao': 0,
            'children': []
        }

        for item in outros_recursos_data:
            node_outros_recursos_total = outros_recursos_total['children']

            if item.get('uuid') == RecursoOpcoesEnum.RECURSO_PROPRIO.name:
                receitas = calcula_receitas_recursos_proprios(item)
                despesas = calcula_despesas_recursos_proprios(item, item.get('prioridades_qs'))
            else:
                receitas_previstas = ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
                    paa=self.paa,
                    outro_recurso_periodo__outro_recurso__uuid=item.get('uuid'),
                )

                receitas = calcula_receitas_outros_recursos(item, receitas_previstas)
                despesas = calcula_despesas_outros_recursos(item, item.get('prioridades_qs'))

            # Último node - Saldo (Custeio, Capital, Livre)
            saldo = self.calcula_saldos(item.get('uuid'), receitas, despesas)

            node_recurso = {
                'key': item.get('uuid'),
                "recurso": item.get('recurso'),
                "custeio": saldo['custeio'],
                "capital": saldo['capital'],
                "livre_aplicacao": saldo['livre_aplicacao'],
                "parent": RecursoOpcoesEnum.OUTRO_RECURSO.name,
                "cor": item.get('cor', None),
                "children": []
            }

            node_outros_recursos_total.append(node_recurso)

            node_recurso['children'].append(receitas)
            node_recurso['children'].append(despesas)
            node_recurso['children'].append(saldo)

            outros_recursos_total['custeio'] += saldo['custeio']
            outros_recursos_total['capital'] += saldo['capital']
            outros_recursos_total['livre_aplicacao'] += saldo['livre_aplicacao']

        return outros_recursos_total

    def resumo_prioridades(self):
        """
            Retorna o resumo das prioridades para o PAA.

            O resumo é um dicionário com as seguintes chaves:
            - PTRF: resumo dos recursos PTRF
            - PDDE: resumo dos recursos PDDE
            - OUTRO_RECURSO: resumo dos outros recursos (Recursos próprios + Outros Recursos)

            Cada chave tem como valor outro dicionário com as seguintes chaves:
            - key: identificador do recurso
            - recurso: descrição do recurso
            - custeio: valor total do custeio
            - capital: valor total do capital
            - livre_aplicacao: valor total da livre aplicação
            - parent: identificação do nível pai da hierarquia do tipo de recurso
            - children: lista de nodes filhos (receitas, despesas e saldos)

            Retorna uma lista com os dados de cada tipo de recurso.
        """

        # Mapa de dados para cada tipo de recurso
        tipo_recurso_map = {
            RecursoOpcoesEnum.PTRF.name: self.calcula_node_ptrf(),
            RecursoOpcoesEnum.PDDE.name: self.calcula_node_pdde(),
            RecursoOpcoesEnum.OUTRO_RECURSO.name: self.calcula_node_outros_recursos(),
        }

        # Retorna a lista de dados para cada tipo de recurso
        dados = list(tipo_recurso_map.values())

        return dados

    def validar_valor_prioridade(self, valor_total, acao_uuid, tipo_aplicacao, recurso, prioridade_uuid=None,
                                 valor_atual_prioridade=None):
        """
        Valida se o valor da prioridade não excede os valores disponíveis de receita.

        Args:
            valor_total (Decimal): Valor total da prioridade em formulário de cadastro/Edição
            acao_uuid (str): UUID da ação (associação ou PDDE) - pode ser None para Recursos Próprios
            tipo_aplicacao (str): Tipo de aplicação (CUSTEIO ou CAPITAL)
            recurso (str): Tipo de recurso (PTRF, PDDE ou RECURSO_PROPRIO)
            prioridade_uuid (str, optional): UUID da prioridade sendo atualizada (para exclusão do cálculo)
            valor_atual_prioridade (Decimal, optional): Valor atual da prioridade sendo atualizada

        Raises:
            serializers.ValidationError: Se o valor exceder os recursos disponíveis
        """

        def obtem_saldos(recurso_data, key_acao):
            """
            Obtém o saldo total disponível para uma ação.

            O saldo total é calculado somando o valor da instância em edição, o valor do Livre Aplicação e
            os valores de custeio e capital (de acordo com o tipo de aplicacao [CUSTEIO ou CAPITAL]).

            Parâmetros:
                recurso_data (dict): Dicionário com os dados da key do
                                    recurso [PTRF, PDDE, RECURSO_PROPRIO ou OUTRO_RECURSO]
                key_acao (str): UUID da ação (associação, PDDE ou Outro Recurso), em caso de Recursos Próprios,
                este valor recebe 'RECURSO_PROPRIO'

            Retorna:
                Decimal: Saldo total disponível para a ação
            """

            # Obtem o Node [PTRF, PDDE, RECURSO_PROPRIO ou OUTRO_RECURSO]
            saldos_resumo = buscar_chave_em_todos_os_niveis(
                recurso_data.get("children", []),
                f"{key_acao}_saldo"
            )

            # Valida se os saldos foram encontrados
            if not saldos_resumo:
                raise serializers.ValidationError(
                    {'mensagem': (
                        f'Saldos de recursos {recurso} não encontrados no resumo de prioridades. '
                        f'(acao_uuid={acao_uuid})')})

            # inicializa o saldo de Livre Aplicação
            saldo_disponivel = saldos_resumo.get('livre_aplicacao')
            logger.info(f"Inicializando saldo disponível de livre aplicacao | acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}, saldo_livre_aplicacao={saldos_resumo.get('livre_aplicacao')}")  # noqa

            # Considera o valor da instância em edição para compor o saldo
            if prioridade_uuid:
                # Considera no saldo o valor da instância em edição
                logger.info(f"Adicionando valor da prioridade instance | acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}, valor_instance={valor_atual_prioridade}, prioridade_uuid={prioridade_uuid}")  # noqa
                saldo_disponivel += valor_atual_prioridade

            # Considera o saldo de Custeio quando tipo de aplicação for CUSTEIO
            if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                logger.info(f"Adicionando saldo de custeio | acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}, saldo_custeio={saldos_resumo.get('custeio')}")  # noqa
                saldo_disponivel += Decimal(saldos_resumo.get('custeio'))

            # Considera o saldo de Capital quando tipo de aplicação for CAPITAL
            if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                logger.info(f"Adicionando saldo de capital | acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}, saldo_capital={saldos_resumo.get('capital')}")  # noqa
                saldo_disponivel += Decimal(saldos_resumo.get('capital'))

            logger.info(f"Saldo disponível calculado | acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}, valor_total={valor_total}, saldo_disponivel={saldo_disponivel}")  # noqa
            return round(saldo_disponivel, 2)

        # Validação de parâmetros
        if valor_total is None or not tipo_aplicacao or not recurso:
            logger.error(f"Erro ao validar valor da prioridade: Parâmetros inválidos | valor_total={valor_total}, acao_uuid={acao_uuid}, tipo_aplicacao={tipo_aplicacao}, recurso={recurso}")  # noqa
            return

        try:
            resumo_data = self.resumo_prioridades()

            recurso_data = buscar_chave_em_todos_os_niveis(resumo_data, recurso) or {}

            if not recurso_data:
                raise serializers.ValidationError(
                    {
                        'mensagem': 'Recurso não encontrado no resumo de prioridades.',
                        'detail': recurso,
                    })

            if recurso == RecursoOpcoesEnum.PTRF.name:
                saldo_disponivel = obtem_saldos(recurso_data, acao_uuid)
                if saldo_disponivel < valor_total:
                    raise ValidacaoSaldoIndisponivel(
                        {
                            'mensagem': (
                                'O valor indicado para a prioridade excede o valor disponível de receita prevista.'),
                            'detail': saldo_disponivel
                        })
                else:
                    return saldo_disponivel

            if recurso == RecursoOpcoesEnum.PDDE.name:
                saldo_disponivel = obtem_saldos(recurso_data, acao_uuid)
                if saldo_disponivel < valor_total:
                    raise ValidacaoSaldoIndisponivel(
                        {
                            'mensagem': (
                                'O valor indicado para a prioridade excede o valor disponível de receita prevista.'),
                            'detail': saldo_disponivel
                        })
                else:
                    return saldo_disponivel

            if recurso == RecursoOpcoesEnum.RECURSO_PROPRIO.name:
                saldo_disponivel = obtem_saldos(recurso_data, RecursoOpcoesEnum.RECURSO_PROPRIO.name)
                if saldo_disponivel < valor_total:
                    raise ValidacaoSaldoIndisponivel(
                        {
                            'mensagem': (
                                'O valor indicado para a prioridade excede o valor disponível de receita prevista.'),
                            'detail': saldo_disponivel
                        })
                else:
                    return saldo_disponivel

            if recurso == RecursoOpcoesEnum.OUTRO_RECURSO.name:
                saldo_disponivel = obtem_saldos(recurso_data, acao_uuid)
                if saldo_disponivel < valor_total:
                    raise ValidacaoSaldoIndisponivel(
                        {
                            'mensagem': (
                                'O valor indicado para a prioridade excede o valor disponível de receita prevista.'),
                            'detail': saldo_disponivel
                        })
                else:
                    return saldo_disponivel
            return

        except serializers.ValidationError as ex:
            logger.error(f"ValidationError ao validar valor da prioridade: {str(ex)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao validar valor da prioridade: {str(e)}")
            raise


def buscar_chave_em_todos_os_niveis(data, key):
    for item in data:
        if item.get("key") == key:
            return item

        children = item.get("children", [])
        if children:
            found = buscar_chave_em_todos_os_niveis(children, key)
            if found:
                return found

    return None
