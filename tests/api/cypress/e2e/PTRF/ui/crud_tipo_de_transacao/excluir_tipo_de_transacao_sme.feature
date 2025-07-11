# language: pt
Funcionalidade: Excluir tipo de transação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar exclusao de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E crio o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de transacao
    E clico no botao "Filtrar" da tela tipos de transacao
    E clico no botao "Editar" da tela tipos de transacao
    E clico no botao "Apagar" da tela tipos de transacao
    E sistema apresenta a '<mensagem_confirmacao_exclusao>' na tela
    Quando clico no botao "Excluir" da tela tipos de transacao
    Entao sistema apresenta a '<mensagem>' na tela

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome       |mensagem_confirmacao_exclusao                    |mensagem                                                        | caso                               |
      | web          | Tipos de Transação          | teste automatizado     |Deseja realmente excluir este tipo de transação? |O tipo de transação foi removido do sistema com sucesso.        |com sucesso                         |