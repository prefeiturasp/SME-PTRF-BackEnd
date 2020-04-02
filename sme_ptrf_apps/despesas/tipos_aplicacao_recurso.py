# Aplicação do Recurso Choice
APLICACAO_CAPITAL = 'CAPITAL'
APLICACAO_CUSTEIO = 'CUSTEIO'

APLICACAO_NOMES = {
    APLICACAO_CAPITAL: 'Capital',
    APLICACAO_CUSTEIO: 'Custeio',
}

APLICACAO_CHOICES = (
    (APLICACAO_CAPITAL, APLICACAO_NOMES[APLICACAO_CAPITAL]),
    (APLICACAO_CUSTEIO, APLICACAO_NOMES[APLICACAO_CUSTEIO]),
)


def aplicacoes_recurso_to_json():
    result = []
    for aplicacao in APLICACAO_CHOICES:
        choice = {
            'id': aplicacao[0],
            'nome': aplicacao[1]
        }
        result.append(choice)
    return result
