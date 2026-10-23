# language: pt
Funcionalidade: Edição Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar edição de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado editado' via API
    E excluo o tipo conta com o nome 'teste automatizado' via API
    E crio o tipo conta com o nome 'teste automatizado' via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dados no campo '<dados_da_pesquisa>' da tela de tipo de conta
    E clico no botao "Pesquisar" da tela tipo de conta
    E clico no botao "Editar" da tela tipo de conta
    E informo dado nos campos "<nome_do_tipo_de_conta>", "<nome_do_banco>", "<n_da_agencia>", "<n_da_conta>", "<n_do_cartao>", "<exibir_os_dados_da_conta_somente_leitura>" e "<conta_permite_encerramento>"
    E clico no botao "Salvar" da tela tipo de conta
    Quando sistema apresenta a '<mensagem>' na tela
    E confirmo que existe exatamente um tipo conta com o nome '<tipo_preservado>' via API
    E confirmo que o tipo conta com o nome '<tipo_ausente>' não existe via API
    Entao excluo e confirmo o tipo conta com o nome '<tipo_preservado>' via API


    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_do_tipo_de_conta       | nome_do_banco      | n_da_agencia | n_da_conta  | n_do_cartao      | exibir_os_dados_da_conta_somente_leitura  | conta_permite_encerramento  | mensagem                                                       | caso                                    | dados_da_pesquisa   | tipo_preservado          | tipo_ausente              |
      | web          | Tipo                        | teste automatizado editado  | teste edicao       | 0002         | 123456      | 1234432112344322 | false                                     | false                       | O tipo de conta foi editado no sistema com sucesso.            | com sucesso                             | teste automatizado   | teste automatizado editado | teste automatizado         |
      | web          | Tipo                        |                           | teste automatizado | 0001         | 12345       | 1234432112344321 | true                                      | true                        | Nome é obrigatório                                             | com nome do tipo de conta em branco     | teste automatizado   | teste automatizado         | teste automatizado editado |
