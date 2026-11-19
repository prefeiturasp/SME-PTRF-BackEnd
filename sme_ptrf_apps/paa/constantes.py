""" Constantes do PAA. A ideia é centralizar e simplificar a mutabilidade
de regras que podem ocorrer após implementação. Dessa forma, não é necessário
alterar trechos de código fonte para alterar regras de negócio.
"""


# Nome da waffle flag utilizada
FLAG_PAA_PROXIMA_VIGENCIA = "paa-proxima-vigencia"


# Modo de validação do mês de elaboração do PAA (ParametroPaa.mes_elaboracao_paa):
# MES_ELABORACAO_IGUAL: só é possível iniciar no próprio mês parametrizado
# MES_ELABORACAO_A_PARTIR_DE: é possível iniciar no mês parametrizado ou depois dele
MES_ELABORACAO_IGUAL = 'IGUAL'
MES_ELABORACAO_A_PARTIR_DE = 'A_PARTIR_DE'
# Valor padrão (requer alteração no configs.js do frontend)
# MODO_MES_ELABORACAO = MES_ELABORACAO_A_PARTIR_DE
MODO_MES_ELABORACAO = MES_ELABORACAO_IGUAL


# Caso, futuramente, o período do PAA compreenda a um períoo fechado do mesmo ano,
# Como achar o período vigente? pelo ano da data inicial (comportamento anterior à implementação)
# ou pela janela [início, fim] que contém hoje.
CRITERIO_PERIODO_VIGENTE_ANO_CORRENTE = 'ANO_CORRENTE'
CRITERIO_PERIODO_VIGENTE_JANELA_DE_DATAS = 'JANELA_DE_DATAS'
# Critério Padrão para achar o período vigente do PAA. Atualmente, o critério é o ano corrente.
# CRITERIO_PERIODO_VIGENTE = CRITERIO_PERIODO_VIGENTE_ANO_CORRENTE
CRITERIO_PERIODO_VIGENTE = CRITERIO_PERIODO_VIGENTE_JANELA_DE_DATAS


# Situação que o PAA vigente deve ter para a associação iniciar o PAA da próxima vigência.
# None: nenhuma exigência (os dois PAAs podem ser elaborados ao mesmo tempo, inclusive sem PAA vigente)
# Tupla de "status_andamento": exige o PAA vigente, exista e esteja em um dos status de andamento listados:
#       exemplo: ('GERADO_PARCIALMENTE', 'GERADO')
STATUS_VIGENTE_EXIGIDOS_PARA_INICIAR_PROXIMA_VIGENCIA = None


# Situação que o PAA ed origem edve ter para suas prioridades serem importadas por outro PAA
# None: Qualquer PAA anterior, inclusive emelaboração
# Tupla de "status_andamento": exige o PAA origem:
#       exemplo: ('GERADO',)
STATUS_PAA_ORIGEM_EXIGIDOS_PARA_IMPORTAR_PRIORIDADES = ('GERADO',)


# Situação que o PAA o período imeiatamente anterior deve ter para o PAA seguinte gerar
# documentos (prévia, Plano Anual e Ata de apresentação).
# None: nenhuma exigência
# TODO: considerar que o PAA exista se houver status, alterar para None
# Tupla de "status_andamento": exige o PAA anterior :
#       exemplo: ('GERADO_PARCIALMENTE', 'GERADO')
STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_GERAR_DOCUMENTOS = None


# Situação que o PAA do período imediatamente anterior deve ter para o PAA seguinte ser retificado.
# TODO: considerar que o PAA exista se houver status
# None: nenhuma exigência (é possível retificar o PAA da Próxima Vigência com o vigente em qualquer situação).
# Tupla de `status_andamento`: exemplo, ('GERADO',) exige o anterior gerado.
STATUS_PAA_ANTERIOR_EXIGIDOS_PARA_RETIFICAR = None


# Constantes para classificar um Período.
# NÃO ALTERAR
VIGENCIA_VIGENTE = 'VIGENTE'
VIGENCIA_PROXIMA_VIGENCIA = 'PROXIMA_VIGENCIA'
VIGENCIA_ENCERRADO = 'ENCERRADO'
VIGENCIA_FUTURO = 'FUTURO'
