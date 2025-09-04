from decimal import Decimal
from rest_framework import serializers
from django.core.exceptions import ValidationError

from sme_ptrf_apps.paa.enums import TipoAplicacaoOpcoesEnum


class PrioridadePaaService:
    """
    Service para validações e cálculos relacionados a PrioridadePaa.
    """
    
    @staticmethod
    def validar_valor_prioridade(attrs):
        """
        Valida se o valor da prioridade não excede os valores disponíveis de receita.
        
        Args:
            attrs (dict): Dados validados do serializer
            
        Raises:
            serializers.ValidationError: Se o valor exceder os recursos disponíveis
        """
        valor_total = attrs.get('valor_total')
        acao_associacao = attrs.get('acao_associacao')
        tipo_aplicacao = attrs.get('tipo_aplicacao')
        
        if valor_total and acao_associacao and tipo_aplicacao:
            try:
                # Importa aqui para evitar importação circular
                from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoRetrieveSerializer
                
                # Obtém dados da ação associação para cálculo dos valores disponíveis
                acao_associacao_data = AcaoAssociacaoRetrieveSerializer(acao_associacao).data
                
                if acao_associacao_data:
                    # Calcula os valores disponíveis para todos os tipos de aplicação
                    valor_custeio = PrioridadePaaService._calcular_valor_disponivel(
                        acao_associacao_data, TipoAplicacaoOpcoesEnum.CUSTEIO.name
                    )
                    valor_capital = PrioridadePaaService._calcular_valor_disponivel(
                        acao_associacao_data, TipoAplicacaoOpcoesEnum.CAPITAL.name
                    )
                    valor_livre = PrioridadePaaService._calcular_valor_livre(acao_associacao_data)
                    
                    valor_prioridade = Decimal(str(valor_total))
                    
                    # Calcula o valor disponível baseado no tipo de aplicação
                    if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
                        valor_disponivel = valor_custeio
                    elif tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
                        valor_disponivel = valor_capital
                    else:
                        valor_disponivel = Decimal('0')
                    
                    # Calcula o valor total disponível (custeio + capital + livre aplicação)
                    valor_total_disponivel = valor_custeio + valor_capital + valor_livre
                    
                    # Verifica se o valor da prioridade excede o valor total disponível
                    if valor_prioridade > valor_total_disponivel:
                        raise serializers.ValidationError(
                            {'mensagem': 'O valor indicado para a prioridade excede o valor disponível de receita prevista.'}
                        )
                    
                    # Verifica se o valor da prioridade excede o valor disponível no tipo específico
                    if valor_prioridade > valor_disponivel:
                        # Se não há saldo suficiente no tipo específico, verifica se há saldo suficiente em livre aplicação
                        if tipo_aplicacao in [TipoAplicacaoOpcoesEnum.CUSTEIO.name, TipoAplicacaoOpcoesEnum.CAPITAL.name]:
                            # Calcula quanto precisa ser usado da livre aplicação
                            valor_necessario_livre = valor_prioridade - valor_disponivel
                            
                            if valor_livre < valor_necessario_livre:
                                # Não há saldo suficiente em livre aplicação, rejeita
                                raise serializers.ValidationError(
                                    {'mensagem': 'O valor indicado para a prioridade excede o valor disponível de receita prevista.'}
                                )
                        else:
                            # Para outros tipos, rejeita se não há saldo suficiente
                            raise serializers.ValidationError(
                                {'mensagem': 'O valor indicado para a prioridade excede o valor disponível de receita prevista.'}
                            )
                        
            except serializers.ValidationError:
                # Re-lança erros de validação
                raise
            except Exception as e:
                # Em caso de erro na validação, permite a operação mas registra o erro
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Erro ao validar valor da prioridade: {str(e)}")

    @staticmethod
    def _calcular_valor_livre(acao_associacao_data):
        """
        Calcula o valor de livre aplicação disponível para uma ação associação.
        Usa a mesma lógica do serviço de resumo de prioridades.
        
        Args:
            acao_associacao_data (dict): Dados da ação associação
            
        Returns:
            Decimal: Valor de livre aplicação disponível
        """
        def get_receita_prevista_da_acao_associacao(acao_associacao_data):
            """Busca as receitas previstas da ação associação"""
            receitas_previstas_paa = acao_associacao_data.get('receitas_previstas_paa', [])
            return receitas_previstas_paa[0] if len(receitas_previstas_paa) else {}

        def calcular_saldos_congelado_atual_previsao(congelado, atual, previsao):
            """Soma saldo congelado (ou atual) com previsão"""
            previsao_valor = Decimal(previsao)
            saldo_congelado = Decimal(congelado)
            saldo_atual = Decimal(atual)
            return (saldo_congelado or saldo_atual) + previsao_valor

        def get_valor_livre(acao_associacao_data):
            """Calcula o valor de livre aplicação baseado nos saldos e previsões"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_livre', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_livre', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_livre', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        return get_valor_livre(acao_associacao_data)

    @staticmethod
    def _calcular_valor_disponivel(acao_associacao_data, tipo_aplicacao):
        """
        Calcula o valor disponível para uma ação associação baseado no tipo de aplicação.
        Usa a mesma lógica do serviço de resumo de prioridades.
        
        Args:
            acao_associacao_data (dict): Dados da ação associação
            tipo_aplicacao (str): Tipo de aplicação (CUSTEIO ou CAPITAL)
            
        Returns:
            Decimal: Valor disponível para o tipo de aplicação
        """
        def get_receita_prevista_da_acao_associacao(acao_associacao_data):
            """Busca as receitas previstas da ação associação"""
            receitas_previstas_paa = acao_associacao_data.get('receitas_previstas_paa', [])
            return receitas_previstas_paa[0] if len(receitas_previstas_paa) else {}

        def calcular_saldos_congelado_atual_previsao(congelado, atual, previsao):
            """Soma saldo congelado (ou atual) com previsão"""
            previsao_valor = Decimal(previsao)
            saldo_congelado = Decimal(congelado)
            saldo_atual = Decimal(atual)
            return (saldo_congelado or saldo_atual) + previsao_valor

        def get_valor_custeio(acao_associacao_data):
            """Calcula o valor de custeio disponível"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_custeio', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_custeio', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_custeio', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        def get_valor_capital(acao_associacao_data):
            """Calcula o valor de capital disponível"""
            receitas_previstas_paa = get_receita_prevista_da_acao_associacao(acao_associacao_data)
            saldos = acao_associacao_data.get('saldos', {})

            previsao_valor = Decimal(receitas_previstas_paa.get('previsao_valor_capital', None) or 0)
            saldo_congelado = Decimal(receitas_previstas_paa.get('saldo_congelado_capital', None) or 0)
            saldo_atual = Decimal(saldos.get('saldo_atual_capital', None) or 0)

            return calcular_saldos_congelado_atual_previsao(saldo_congelado, saldo_atual, previsao_valor)

        # Retorna o valor disponível baseado no tipo de aplicação
        if tipo_aplicacao == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
            return get_valor_custeio(acao_associacao_data)
        elif tipo_aplicacao == TipoAplicacaoOpcoesEnum.CAPITAL.name:
            return get_valor_capital(acao_associacao_data)
        else:
            return Decimal('0')
