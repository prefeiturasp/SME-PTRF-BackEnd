import logging

from sme_ptrf_apps.core.models import PrestacaoConta

class BemProduzidoService:
    """
    Service para regras de negócio relacionadas a Bens Produzidos
    """

    @staticmethod
    def verificar_se_pode_informar_valores(despesas):
        """
        Verifica se há pelo menos uma despesa que permite informar valores em situação patrimonial.
        
        Regra:
        - Se TODAS as despesas são de períodos finalizados com PC entregue: não permite (retorna False)
        - Se há pelo menos uma despesa de período não finalizado OU período finalizado sem PC entregue: permite (retorna True)
        
        Args:
            despesas: QuerySet ou lista de objetos Despesa
            
        Returns:
            dict: {
                'pode_informar_valores': bool,
                'mensagem': str
            }
        """
        if not despesas:
            return {
                'pode_informar_valores': False,
                'mensagem': 'Nenhuma despesa fornecida para verificação.'
            }

        status_pc_entregue = [
            status for status in PrestacaoConta.STATUS_NOMES.keys() 
            if status != PrestacaoConta.STATUS_NAO_APRESENTADA
        ]

        todas_despesas_periodo_finalizado_com_pc = True

        for despesa in despesas:
            periodo = despesa.periodo_da_despesa
            
            if not periodo or not despesa.associacao:
                # Despesa sem período ou associação: permite adicionar
                todas_despesas_periodo_finalizado_com_pc = False
                break
            
            if not periodo.encerrado:
                # Período não finalizado: permite adicionar
                todas_despesas_periodo_finalizado_com_pc = False
                break
            
            # Período finalizado: verificar se há PC entregue
            pc = PrestacaoConta.objects.filter(
                periodo=periodo,
                associacao=despesa.associacao
            ).first()
            
            if not pc or pc.status not in status_pc_entregue:
                # Período finalizado SEM PC entregue: permite adicionar
                todas_despesas_periodo_finalizado_com_pc = False
                break

        # Se todas as despesas são de períodos finalizados com PC entregue, NÃO permite
        pode_informar_valores = not todas_despesas_periodo_finalizado_com_pc

        if pode_informar_valores:
            mensagem = 'Há pelo menos uma despesa de período não finalizado ou sem prestação de contas entregue.'
        else:
            mensagem = 'Todas as despesas são de períodos finalizados com prestação de contas entregue.'

        return {
            'pode_informar_valores': pode_informar_valores,
            'mensagem': mensagem
        }

