# language: pt

Funcionalidade: Consultar créditos da escola

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar exibição do: <caso>
    Quando clico na opção Créditos da escola
    Então sistema exibe "<campo>" nos créditos da UE

    Exemplos:
      | visualizacao | campo                 |      caso                   |
      | web          | sem_filtros_aplicados | Valor sem filtros aplicados |
      | web          | filtros_aplicados     | Valor filtros aplicados     |
      | web          | tipo                  | Tipo do crédito             |
      | web          | conta                 | Conta creditada             |
      | web          | acao                  | Ação do crédito             |
      | web          | data                  | Data do lançamento          |
      | web          | valor                 | Valor do crédito            |

  Esquema do Cenário: Validar soma dos créditos: <caso>
    Quando clico na opção Créditos da escola
    Então valida os totais de créditos da UE

    Exemplos:
      | visualizacao | caso                  |
      | web          | Com filtros aplicados |
      | web          | Sem filtros aplicados |

  Esquema do Cenário: Validar filtro por tipo de crédito: <caso>
    Quando clico na opção Créditos da escola
    E seleciono o filtro por tipo "<campo>"
    Então sistema filtra por tipo "<campo>" nos créditos da UE

    Exemplos:
      | visualizacao | campo      | caso              |
      | web          | devolucao  | Devolução à conta |
      | web          | estorno    | Estorno           |
      | web          | externo    | Recurso externo   |
      | web          | rendimento | Rendimento        |
      | web          | repasse    | Repasse           |
      | web          | todas      | Todas             |

  Esquema do Cenário: Validar total de créditos da UE: <caso>
    Quando clico na opção Créditos da escola
    Então sistema valida o total filtrado de repasse nos créditos da UE

    Exemplos:
      | visualizacao | caso              |
      | web          | Filtros aplicados |

  Esquema do Cenário: Validar em mais filtros: <caso>
    Quando clico na opção Créditos da escola
    E aciono mais filtros em créditos da escola
    E preencho os filtros de créditos da escola conforme o caso "<caso>"
    Então sistema filtra os créditos da UE conforme "<caso>"

    Exemplos:
      | visualizacao | caso                     |
      | web          | Detalhamento do crédito  |
      | web          | Conta                    |
      | web          | Ação                     |
      | web          | Período de               |
      | web          | Período até              |

  Esquema do Cenário: Validar todos os filtros de: <caso>
    Quando clico na opção Créditos da escola
    E aciono mais filtros em créditos da escola
    E preencho o filtro detalhamento do crédito com "Fevereiro"
    E preencho o filtro conta com "Cheque"
    E preencho o filtro ação com "PTRF Básico"
    E preencho o filtro período de com "01/01/2026"
    E preencho o filtro período até com "31/12/2026"
    Então sistema filtra os dados com todos os filtros nos créditos da UE

    Exemplos:
      | visualizacao | caso               |
      | web          | Créditos da escola |

  Esquema do Cenário: Validar botão: <caso>
    Quando clico na opção Créditos da escola
    Então sistema valida o botão "<botão>" nos créditos da UE

    Exemplos:
      | visualizacao | botão        | caso           |
      | web          | limpa filtro | Limpar filtros |
      | web          | cancela      | Cancelar       |

  Esquema do Cenário: Validar abrir a : <caso>
    Quando clico na opção Créditos da escola
    Então abre a exibição no botão "<botão>" nos créditos da UE

    Exemplos: 
      | visualizacao | botão                 | caso                              |
      | web          | valores reprogramados | Consulta de valores reprogramados |

  Esquema do Cenário: Validar valores reprogramados: <caso>
    Quando clico na opção Créditos da escola
    E abro a tela de valores reprogramados nos créditos da UE
    Então sistema valida a soma os valores reprogramados da UE

    Exemplos:
      | visualizacao | caso  |
      | web          | Total |