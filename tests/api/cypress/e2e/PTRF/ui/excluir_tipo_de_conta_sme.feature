# language: pt
Funcionalidade: Excluir Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar exclusâo de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    E crio o tipo conta com o nome 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dados no campo '<dados_da_pesquisa>' da tela de tipo de conta
    E clico no botao "Pesquisar" da tela tipo de conta
    E clico no botao "Editar" da tela tipo de conta
    E clico no botao "Apagar tipo de conta" da tela tipo de conta
    E sistema apresenta a "<mensagem_de_confirmacao_de_erro>" para afirmacao da exclusao do tipo de conta
    Quando clico no botao "Excluir" da tela tipo de conta
    Entao sistema apresenta a '<mensagem>' na tela


    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | mensagem                                                       | caso        | mensagem_de_confirmacao_de_erro               | dados_da_pesquisa   |
      | web          | Tipo                        |  O tipo de conta foi removido do sistema com sucesso.          | com sucesso | Deseja realmente excluir este Tipo de Conta?  | teste automatizado  |
