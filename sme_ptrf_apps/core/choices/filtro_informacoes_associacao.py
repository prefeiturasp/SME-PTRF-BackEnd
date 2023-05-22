class FiltroInformacoesAssociacao:
    FILTRO_INFORMACOES_ENCERRADAS = "ENCERRADAS"
    FILTRO_INFORMACOES_NAO_ENCERRADAS = "NAO_ENCERRADAS"

    FILTRO_INFORMACOES_ASSOCIACAO_CHOICE = (
        (FILTRO_INFORMACOES_ENCERRADAS, "Encerradas"),
        (FILTRO_INFORMACOES_NAO_ENCERRADAS, "Não encerradas")
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
