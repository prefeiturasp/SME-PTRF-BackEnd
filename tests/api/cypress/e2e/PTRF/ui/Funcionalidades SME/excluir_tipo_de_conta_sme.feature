# language: pt
Funcionalidade: Excluir Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar exclusâo de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' via API
    E crio o tipo conta com o nome 'teste automatizado' via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dados no campo '<dados_da_pesquisa>' da tela de tipo de conta
    E clico no botao "Pesquisar" da tela tipo de conta
    E clico no botao "Editar" da tela tipo de conta
    E clico no botao "Apagar tipo de conta" da tela tipo de conta
    E sistema apresenta a "<mensagem_de_confirmacao_de_erro>" para afirmacao da exclusao do tipo de conta
    Quando clico no botao "Excluir" da tela tipo de conta
    E sistema apresenta a '<mensagem>' na tela
    Entao confirmo que o tipo conta com o nome 'teste automatizado' não existe via API


    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | mensagem                                                       | caso        | mensagem_de_confirmacao_de_erro               | dados_da_pesquisa   |
      | web          | Tipo                        |  O tipo de conta foi removido do sistema com sucesso.          | com sucesso | Deseja realmente excluir este tipo de conta?  | teste automatizado  |
