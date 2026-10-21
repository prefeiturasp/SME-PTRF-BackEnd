import logging
from sme_ptrf_apps.core.models import PrestacaoConta, Periodo
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from django.db import transaction


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

    @staticmethod
    def obter_despesa_mais_recente(despesas):
        """Retorna a despesa mais recente pela data de transação."""
        candidatas = []
        for despesa in despesas:
            if despesa is None or despesa.data_transacao is None:
                continue
            candidatas.append((despesa.data_transacao, despesa))

        if not candidatas:
            return None

        candidatas.sort(key=lambda item: item[0])
        return candidatas[-1][1]

    @staticmethod
    def periodo_da_despesa_esta_fechado(despesa, associacao) -> bool:
        """
        Período fechado: período encerrado e prestação de contas entregue
        (status diferente de não apresentada).
        """
        if not despesa or not associacao:
            return False

        periodo = despesa.periodo_da_despesa
        if periodo is None and despesa.data_transacao:
            periodo = Periodo.da_data_por_recurso(despesa.data_transacao, despesa.recurso)

        if not periodo or not periodo.encerrado:
            return False

        prestacao_conta = PrestacaoConta.by_periodo(
            associacao=associacao,
            periodo=periodo,
        )
        if prestacao_conta is None:
            return False

        return prestacao_conta.status != PrestacaoConta.STATUS_NAO_APRESENTADA

    @staticmethod
    def bem_produzido_em_modo_visualizacao(bem_produzido: BemProduzido) -> bool:
        """
        True somente para bem completo cuja despesa mais recente está em período fechado.

        Rascunho permanece editável. O impedimento de período fechado, nesse caso,
        ocorre na tela ao tentar informar valores.
        """
        if bem_produzido is None or not bem_produzido.associacao_id:
            return False

        if bem_produzido.status != BemProduzido.STATUS_COMPLETO:
            return False

        despesas = [
            vinculo.despesa
            for vinculo in bem_produzido.despesas.select_related("despesa").all()
        ]
        despesa_mais_recente = BemProduzidoService.obter_despesa_mais_recente(despesas)
        if despesa_mais_recente is None:
            return False

        return BemProduzidoService.periodo_da_despesa_esta_fechado(
            despesa_mais_recente,
            bem_produzido.associacao,
        )

    @staticmethod
    def validacoes_edicao_bem_produzido(bem_produzido: BemProduzido, validated_data=None) -> None:
        """
        Executa as validações de negócio para a edição de um bem produzido.

        Constrói o contexto a partir do bem e dos dados informados na edição
        e executa a pipeline de edição. Campos ausentes no payload permanecem
        os da instância.

        Args:
            bem_produzido (BemProduzido): Bem produzido a ser validado.
            validated_data (dict, optional): Dados da edição já validados pelo serializer.

        Raises:
            SituacaoPatrimonialValidationError: Se o bem produzido não atender
                às regras de negócio para edição.
        """
        from sme_ptrf_apps.situacao_patrimonial.validators import (
            BemProduzidoContextBuilder,
            EDIT_PIPELINE,
        )

        context = BemProduzidoContextBuilder.build(
            bem_produzido=bem_produzido,
            validated_data=validated_data,
        )

        EDIT_PIPELINE.run(context)

    @staticmethod
    def validacoes_delecao_bem_produzido(bem_produzido: BemProduzido) -> None:
        """
        Executa as validações de negócio para a exclusão de um bem produzido.

        Constrói o contexto de validação a partir do bem produzido e dos
        períodos relacionados às suas despesas, executando o pipeline de
        validação de exclusão.

        Args:
            bem_produzido (BemProduzido): Bem produzido a ser validado.

        Raises:
            SituacaoPatrimonialValidationError: Se o bem produzido não atender
                às regras de negócio para exclusão.
        """
        from sme_ptrf_apps.situacao_patrimonial.validators import (
            BemProduzidoContextBuilder,
            DELETE_PIPELINE,
        )

        recurso = bem_produzido.recurso

        periodos_despesas = []

        for item in bem_produzido.despesas.all():
            if not item.despesa.data_transacao:
                continue

            periodo = Periodo.da_data_por_recurso(
                item.despesa.data_transacao,
                recurso,
            )

            if periodo is not None:
                periodos_despesas.append(periodo)

        context = BemProduzidoContextBuilder.build(
            bem_produzido=bem_produzido,
            periodos=periodos_despesas,
        )

        DELETE_PIPELINE.run(context)

    @staticmethod
    def verificar_se_pode_excluir_bem_produzido(bem_produzido: BemProduzido) -> str:
        """
        Verifica se um bem produzido pode ser excluído.

        Executa as validações de negócio para a exclusão e retorna uma
        mensagem indicando que a operação é permitida quando nenhuma
        restrição é encontrada.

        Args:
            bem_produzido (BemProduzido): Bem produzido a ser verificado.

        Returns:
            str: Mensagem indicando que o bem produzido pode ser excluído.

        Raises:
            SituacaoPatrimonialValidationError: Se o bem produzido não atender
                às regras de negócio para exclusão.
        """

        BemProduzidoService.validacoes_delecao_bem_produzido(bem_produzido)

        return "O bem produzido pode ser excluído."

    @staticmethod
    @transaction.atomic
    def excluir_bem_produzido(bem_produzido) -> str:
        """
        Exclui um bem produzido.

        Executa as validações de negócio e, caso todas sejam satisfeitas,
        realiza a exclusão do bem produzido em uma transação atômica.

        Args:
            bem_produzido (BemProduzido): Bem produzido a ser excluído.

        Returns:
            str: Mensagem indicando que a exclusão foi realizada com sucesso.

        Raises:
            SituacaoPatrimonialValidationError: Se o bem produzido não atender
                às regras de negócio para exclusão.
        """
        BemProduzidoService.validacoes_delecao_bem_produzido(bem_produzido)

        bem_produzido.delete()

        return 'O bem produzido foi excluído com sucesso.'
