# language: pt
Funcionalidade: Cadastro Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar cadastro de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>" 
    E clico no botao "Adicionar tipo de conta" da tela tipo de conta
    E informo dado nos campos "<nome_do_tipo_de_conta>", "<nome_do_banco>", "<n_da_agencia>", "<n_da_conta>", "<n_do_cartao>", "<exibir_os_dados_da_conta_somente_leitura>" e "<conta_permite_encerramento>"
    E clico no botao "Salvar" da tela tipo de conta
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_do_tipo_de_conta | nome_do_banco      | n_da_agencia | n_da_conta | n_do_cartao      | exibir_os_dados_da_conta_somente_leitura | conta_permite_encerramento | mensagem                                                       | caso                                    |
      | web          | Tipo                        |   teste automatizado  | teste automatizado | 0001         | 12345      | 1234432112344321 | true                                     | true                       |  O tipo de conta foi adicionado ao sistema com sucesso.        | com sucesso                             | 
      | web          | Tipo                        |                       | teste automatizado | 0001         | 12345      | 1234432112344321 | true                                     | true                       |  Nome é obrigatório                                            | com nome do tipo de conta em branco     | 

  Esquema do Cenário: Validar cadastro de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    E crio o tipo conta com o nome 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>" 
    E clico no botao "Adicionar tipo de conta" da tela tipo de conta
    E informo dado nos campos "<nome_do_tipo_de_conta>", "<nome_do_banco>", "<n_da_agencia>", "<n_da_conta>", "<n_do_cartao>", "<exibir_os_dados_da_conta_somente_leitura>" e "<conta_permite_encerramento>"
    E clico no botao "Salvar" da tela tipo de conta
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_do_tipo_de_conta | nome_do_banco      | n_da_agencia | n_da_conta | n_do_cartao      | exibir_os_dados_da_conta_somente_leitura | conta_permite_encerramento | mensagem                                          | caso                                    |
      | web          | Tipo                        |   teste automatizado  | teste automatizado | 0001         | 12345      | 1234432112344321 | true                                     | true                       |  Já existe um tipo de conta com esse nome.        | registro já cadastrado                  | 