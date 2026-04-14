# language: pt

Funcionalidade: Edição de dados das contas da associação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar edição de dados das contas: <caso>
    Quando carrega os dados das contas
    E altero o "<campo>" conta da associação
    Então sistema altera os dados das contas na tela

    Exemplos:
      | visualizacao | campo    | caso                |
      | web          | banco    | Alterar banco       |
      | web          | agencia  | Alterar agência     |
      | web          | conta    | Alterar nº da conta |
  
  Esquema do Cenário: Validar cancelar edição de dados das contas: <caso>
    Quando carrega os dados das contas
    E clico no "<campo>" conta da associação
    Então sistema não altera os dados das contas na tela

    Exemplos:
      | visualizacao | campo    | caso               |
      | web          | cancelar | Clicar em cancelar |

  Esquema do Cenário: Validar encerramento da conta: <caso>
    Quando clico em dados das contas
    E clico em "<botao>" conta da associação
    Então sistema envia a solicitação dos dados das contas

    Exemplos:
      | visualizacao | botao                         | caso                                   |
      | web          | solicita_encerramento         | Enviar solicitação                     |
      | web          | cancelar_modal_solicitado     | Cancelar no modal mantendo solicitação |
      | web          | cancela_solicitacao           | Cancelar solicitação                   |



    

