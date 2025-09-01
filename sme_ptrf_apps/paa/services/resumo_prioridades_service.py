from decimal import Decimal
from django.db.models import Sum
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum


class ResumoPrioridadesService:
    def __init__(self, paa):
        self.paa = paa

    def calcula_despesa_livre_aplicacao(self, despesa_custeio, despesa_capital, receita_custeio, receita_capital):
        """
            Calcula a despesa livre de aplicação com base na diferença de valores das receitas e despesas informadas.

            A lógica utilizada é a seguinte:
            - Se a receita de custeio for menor que a despesa de custeio,
            subtrai a despesa de custeio da receita de custeio e soma a diferença à
            coluna Livre Aplicação de Despesas.(de onde será utilizado o valor não suprido pela receita)
            - De forma igual, também, para receitas e despesas de capital
        """
        despesa_livre = 0

        # Soma a diferença à coluna Livre Aplicação de Despesas quando não há valor suficiente de receitas para Custeio
        diferenca_custeio = receita_custeio - despesa_custeio
        despesa_livre += (diferenca_custeio * -1) if diferenca_custeio <= 0 else 0

        # Soma a diferença à coluna Livre Aplicação de Despesas quando não há valor suficiente de receitas para Capital
        diferenca_capital = receita_capital - despesa_capital
        despesa_livre += (diferenca_capital * -1) if diferenca_capital <= 0 else 0

        return despesa_livre

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

        # O valor total de capitral não deve exibir o saldo negativo (considerando que a diferença seja
        #  utilizada, também, em livre aplicação)
        total_capital = receitas['capital'] - despesas['capital']
        total_capital = total_capital if total_capital > 0 else 0

        # Calculo do total de Livre Aplicação
        total_livre = receitas['livre_aplicacao'] - despesas['livre_aplicacao']

        return {
            'key': key + '_' + 'saldo',
            "recurso": 'Saldo',
            "custeio": total_custeio,
            "capital": total_capital,
            "livre_aplicacao": total_livre,
        }

    def calcula_node_ptrf(self) -> dict:
        from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoRetrieveSerializer

        # Queryset Somente de Prioridades do PAA do recurso PTRF
        prioridades_ptrf_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.PTRF.name,
            prioridade=True)

        # Queryset de Ações de Associação do PAA ordenados por nome da Ação
        acoes_associacoes_qs = self.paa.associacao.acoes.order_by('acao__nome')

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
                # Verificar se existe retorno de receitas previstas em Acao Associacao
                receitas_previstas_paa = acao_associacao_data.get('receitas_previstas_paa', [])
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

            receita_custeio = receitas['custeio']
            receita_capital = receitas['capital']

            # "O sistema deve exibir nas despesas previstas o valor total das
            # prioridades cadastradas de Capital e Custeio que utilizaram o saldo de Livre Aplicação"
            despesa_livre = 0

            despesa_livre += self.calcula_despesa_livre_aplicacao(
                despesa_custeio,
                despesa_capital,
                receita_custeio,
                receita_capital
            )
            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": despesa_livre,
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
            recurso=RecursoOpcoesEnum.PDDE.name,
            prioridade=True
        )

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

            receita_custeio = receitas['custeio']

            receita_capital = receitas['capital']

            # "O sistema deve exibir nas despesas previstas o valor total das
            # prioridades cadastradas de Capital e Custeio que utilizaram o saldo de Livre Aplicação"
            despesa_livre = 0

            despesa_livre += self.calcula_despesa_livre_aplicacao(
                despesa_custeio,
                despesa_capital,
                receita_custeio,
                receita_capital
            )

            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": despesa_livre,
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

    def calcula_node_recursos_proprios(self) -> dict:
        """
            Retorna o resumo das prioridades para o PAA de Recursos Próprios.

            O resumo é um dicionário com as seguintes chaves:
            - key: identificador do recurso
            - recurso: descrição do recurso
            - custeio: valor total do custeio
            - capital: valor total do capital
            - livre_aplicacao: valor total da livre aplicação
            - parent: identificação do nível pai da hierarquia do tipo de recurso
            - children: lista de nodes filhos (receitas, despesas e saldos)

            O item Recursos Próprios deve agrupar seus respectivos filhos e considerar apenas seus valores totalizados
            pelo level 2 (receita, despesas previstas e saldo), uma vez que, as despesas previstas de
            Recursos Próprios apresentariam replicadas para cada linha de um item de Recursos Próprios

            Retorna um dicionário com a estrutura do Node Pai para montagem de tabela de hierarquias no frontend.
            Node 1: Recursos Próprios
                - Node 2: Item Recursos Próprios (level oculto no frontend)
                    - Node 3: Receitas
                    - Node 3: Despesas previstas
                    - Node 3: Saldo
        """

        from sme_ptrf_apps.paa.api.serializers import RecursoProprioPaaListSerializer

        # Queryset Somente de Prioridades do PAA de Recursos Próprios
        prioridades_recurso_proprio_qs = self.paa.prioridadepaa_set.filter(
            recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            prioridade=True)

        # Queryset de instâncias de recursos próprios ordenados pela descrição
        recurso_proprio_qs = self.paa.recursopropriopaa_set.all().order_by('descricao')

        # Dados de Recursos Próprios Serializados
        recurso_proprio_data = RecursoProprioPaaListSerializer(recurso_proprio_qs, many=True).data

        # Agrupar os valores de prioridades de Recursos Próprios
        # Considerar regra de negócio, exclusivamente, para não exibir itens de Recursos Próprios separadamente
        # O item Recursos Próprios deve agrupar seus respectivos filhos e considerar apenas seus valores totalizados
        # pelo level 2 (receita, despesas previstas e saldo), uma vez que, as despesas previstas de
        # Recursos Próprios apresentariam replicadas para cada linha de um item de Recursos Próprios
        recurso_proprio_data = [{
            'uuid': 'item_recursos',
            'descricao': 'Total de Recursos Próprios',
            'valor': sum(item['valor'] for item in recurso_proprio_data)
        }]

        def calcula_receitas(item) -> dict:
            """
                Calcula as receitas de um item de Recursos Próprios para montagem de tabela de hierarquias no frontend.
                Retorna um dicionário com a estrutura do Node 3 de "Receita".
                :param item: Dado de um item de Recursos Próprios para compor o dict de retorno
                :return: Dicionário com a estrutura do Node 3 de Receita
            """

            def get_valor_livre(item) -> Decimal:
                """
                    Retorna o valor de livre aplicação de um item de Recursos Próprios.
                    :param item: Dado de um item de Recursos Próprios
                    :return: Decimal com o valor de receita de livre aplicação
                """
                return Decimal(item.get('valor') or 0)

            return {
                'key': item.get('uuid') + '_' + 'receita',
                "recurso": 'Receita',
                "custeio": Decimal(0),
                "capital": Decimal(0),
                "livre_aplicacao": get_valor_livre(item),
            }

        def calcula_despesas(item, receitas) -> dict:
            """
                Calcula as despesas previstas de um item de Recursos Próprios para montagem de tabela de
                hierarquias no frontend.
                :param item: Dado de um item de Recursos Próprios para compor o dict de retorno
                :param receitas: Dicionário com informações de despesas previstas de Recursos Próprios
                :return: Dicionário com a estrutura do Node 3 de "Despesas previstas".
            """

            # Valores relacionados às "Prioridades do PAA" de Recurso Próprio e tipo CUSTEIO
            despesa_custeio = prioridades_recurso_proprio_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            # Valores relacionados às "Prioridades do PAA" de Recurso Próprio e tipo CAPITAL
            despesa_capital = prioridades_recurso_proprio_qs.filter(
                tipo_aplicacao=TipoAplicacaoOpcoesEnum.CAPITAL.name,
                acao_pdde__isnull=True,
                acao_associacao__isnull=True,
            ).aggregate(
                total=Sum('valor_total')
            ).get('total') or 0

            receita_custeio = receitas['custeio']

            receita_capital = receitas['capital']

            # "O sistema deve exibir nas despesas previstas o valor total das
            # prioridades cadastradas de Capital e Custeio que utilizaram o saldo de Livre Aplicação"
            despesa_livre = 0

            despesa_livre += self.calcula_despesa_livre_aplicacao(
                despesa_custeio,
                despesa_capital,
                receita_custeio,
                receita_capital
            )
            return {
                'key': item.get('uuid') + '_' + 'despesa',
                "recurso": 'Despesas previstas',
                "custeio": despesa_custeio,
                "capital": despesa_capital,
                "livre_aplicacao": despesa_livre,
            }

        # Estrutura do Node Pai para montagem de tabela de hierarquias no frontend
        # Node 1
        tipo_recurso_map = {
            'key': RecursoOpcoesEnum.RECURSO_PROPRIO.name,
            'recurso': 'Recursos Próprios',
            'custeio': 0,
            'capital': 0,
            'livre_aplicacao': 0,
            'children': []
        }

        # Obter a lista de Recursos Próprios do PAA, serializada
        for item in recurso_proprio_data:
            # hierarquia filhos do Node Pai
            children = tipo_recurso_map['children']

            # Node 3 - Valores da Receita (Custeio, Capital, Livre)
            receitas = calcula_receitas(item)

            # Node 3 - Valores da Despesas (Custeio, Capital, Livre)
            despesas = calcula_despesas(item, receitas)

            # Node 3 - Valores Saldo
            saldo = self.calcula_saldos(item.get('uuid'), receitas, despesas)

            # Node 2 - Item Recursos Próprios
            node = {
                'key': item.get('uuid'),
                "recurso": item.get('descricao'),
                "custeio": saldo['custeio'],
                "capital": saldo['capital'],
                "livre_aplicacao": saldo['livre_aplicacao'],
                "parent": RecursoOpcoesEnum.RECURSO_PROPRIO.name,
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

    def resumo_prioridades(self):
        """
            Retorna o resumo das prioridades para o PAA.

            O resumo é um dicionário com as seguintes chaves:
            - PTRF: resumo dos recursos PTRF
            - PDDE: resumo dos recursos PDDE
            - RECURSO_PROPRIO: resumo dos recursos próprios

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
            RecursoOpcoesEnum.RECURSO_PROPRIO.name: self.calcula_node_recursos_proprios(),
        }

        # Retorna a lista de dados para cada tipo de recurso
        dados = [tipo_recurso_map[recurso.name] for recurso in RecursoOpcoesEnum]

        return dados
