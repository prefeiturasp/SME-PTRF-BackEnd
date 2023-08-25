class FiltroInformacoesAssociacao:
    FILTRO_INFORMACOES_ENCERRADAS = "ENCERRADAS"
    FILTRO_INFORMACOES_ENCERRAMENTO_CONTA_PENDENTE = "ENCERRAMENTO_CONTA_PENDENTE"

    FILTRO_INFORMACOES_ASSOCIACAO_CHOICE = (
        (FILTRO_INFORMACOES_ENCERRADAS, "Associações encerradas"),
        (FILTRO_INFORMACOES_ENCERRAMENTO_CONTA_PENDENTE, "Encerramento de conta pendente")
    )

    @classmethod
    def choices(cls):
        result = []
        for choice in cls.FILTRO_INFORMACOES_ASSOCIACAO_CHOICE:
            informacoes = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(informacoes)
        return result
