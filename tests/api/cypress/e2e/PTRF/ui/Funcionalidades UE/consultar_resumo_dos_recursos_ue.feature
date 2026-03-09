# language: pt
Funcionalidade: Consulta de resumo dos recursos

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar a exibição do resumo: <caso>
    E clico no menu Resumo dos recursos
    Quando seleciono o período do quadrimestre "<campo>"
    Então sistema retorna na tela de resumo

    Exemplos:
      | visualizacao | campo     | caso              |
      | web          | atual     | Período atual     |
      | web          | anterior  | Período anterior  |
      | web          | penultimo | Período penúltimo |

  Esquema do Cenário: Validar a exibição de: <caso>
    E clico no menu Resumo dos recursos
    Quando seleciono a conta no quadrimestre "<campo>"
    Então sistema retorna na tela de resumo

    Exemplos:
      | visualizacao | campo  | caso            |
      | web          | todas   | Todas as contas |
      | web          | cheque | Cheque          |
      | web          | cartao | Cartão          |

  Esquema do Cenário: Validar a exibição do card: <caso>
    E clico no menu Resumo dos recursos
    Quando verifico o card "<caso>" do recurso
    Então o sistema deve exibir o card na tela Resumo dos recursos

    Exemplos:
      | caso                       |
      | PTRF Básico                |
      | Rolê Cultural              |
      | Formação                   |
      | Material Pedagógico        |
      | Salas e Espaços de Leitura |
      | Material Complementar      |
      | Recurso Externo            |

  Esquema do Cenário: Validar a exibição de saldos: <caso>
    E clico no menu Resumo dos recursos
    Quando verifico o saldo de cada recurso
    Então o sistema deve exibir o card na tela Resumo dos recursos

    Exemplos:
      | caso                       |
      | PTRF Básico                |
      | Rolê Cultural              |
      | Formação                   |
      | Material Pedagógico        |
      | Salas e Espaços de Leitura |
      | Material Complementar      |
      | Recurso Externo            |

  Esquema do Cenário: Validar o saldo reprogramado: <caso>
    E clico no menu Resumo dos recursos
    Quando verifico o saldo no campo total do recurso
    Então valida que é igual reprogramado da tela Resumo dos recursos

    Exemplos:
      | caso                       |
      | PTRF Básico                |
      | Rolê Cultural              |
      | Formação                   |
      | Material Pedagógico        |
      | Salas e Espaços de Leitura |
      | Material Complementar      |
      | Recurso Externo            |