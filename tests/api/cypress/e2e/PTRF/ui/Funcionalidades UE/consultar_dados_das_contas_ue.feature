# language: pt
Funcionalidade: Consulta de dados das contas da associação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar exibição de dados das contas: <caso>
    Quando clico na opção Dados das contas
    Então sistema retorna na tela de contas "<campo>"

    Exemplos:
      | visualizacao | campo         | caso                     |
      | web          | conta_1       | Conta 1                  |
      | web          | conta_2       | Conta 2                  |
      | web          | banco         | Banco                    |
      | web          | tipo_de_conta | Tipo de Conta            |
      | web          | agencia       | Agência                  |
      | web          | numero_conta  | Nº da conta com o dígito |
      | web          | saldo         | Saldo de Recursos        |

  Esquema do Cenário: Validar exportação em dados das contas: <caso>
    E clico na opção Dados das contas
    Quando clico para exportar na tela de contas "<botao>"
    Então sistema exporta os dados de contas

    Exemplos:
      | visualizacao | botao               | caso             |
      | web          | dados da associação | Dados exportados |
      | web          | ficha cadastral     | Ficha exportada  |

  Esquema do Cenário: Validar os dados das contas: <caso>
    Quando clico na opção Dados das contas
    Então valida na tela dados de contas da associação "<associacao_id>"

    Exemplos:
      | visualizacao | associacao_id |  caso                    | 
      | web          | 1657          | Validar dados da conta 1 | 
      | web          | 1657          | Validar dados da conta 2 |

  Esquema do Cenário: Validar os dados das contas: <caso>
    Quando clico na opção Dados das contas
    Então o saldo de contas da associação

    Exemplos:
      | visualizacao | caso                         | 
      | web          | Saldo de Recursos da Conta 1 | 
      | web          | Saldo de Recursos da Conta 2 |
      
