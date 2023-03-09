
class AnaliseLancamentoPrestacaoContaService:

    @classmethod
    def marcar_devolucao_tesouro_como_atualizada(cls, analise_lancamento):
        return analise_lancamento.passar_devolucao_tesouro_para_atualizada()

    @classmethod
    def marcar_devolucao_tesouro_como_nao_atualizada(cls, analise_lancamento):
        return analise_lancamento.passar_devolucao_tesouro_para_nao_atualizada()

    @classmethod
    def marcar_lancamento_como_atualizado(cls, analise_lancamento):
        return analise_lancamento.passar_lancamento_para_atualizado()

    @classmethod
    def marcar_lancamento_como_excluido(cls, analise_lancamento):
        return analise_lancamento.passar_lancamento_para_excluido()

    @classmethod
    def marcar_lancamento_como_conciliado(cls, analise_lancamento, periodo):
        return analise_lancamento.passar_lancamento_para_conciliado(periodo)

    @classmethod
    def marcar_lancamento_como_desconciliado(cls, analise_lancamento):
        return analise_lancamento.passar_lancamento_para_desconciliado()
