# language: pt
Funcionalidade: Excluir fornecedor

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "DRE"

  Esquema do Cenário: Validar exclusão de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado" via API
    E crio o fornecedor com o nome 'teste automatizado' e "<valores_consulta_cpf_cnpj>" via API
    E clico na opcao "Fornecedores" com a visao SME
    E informo dado nos campos "<nome_do_fornecedor>" e "<cpf_cnpj>" para pesquisa na tela de Fornecedores
    E clico no botao "Filtrar" da tela Fornecedores
    E clico no botao "Editar" da tela fornecedor na tabela com a opcao 'teste automatizado'
    E clico no botao "Apagar" da tela Fornecedores
    E sistema apresenta a "<mensagem_de_confirmacao_de_erro>" para afirmacao da exclusao
    Quando clico no botao "Excluir" da tela Fornecedores
    E sistema apresenta a '<mensagem>' na tela
    Entao confirmo que o fornecedor com o nome "teste automatizado" não existe via API

    Exemplos:
      | visualizacao | nome_do_fornecedor | cpf_cnpj              |valores_consulta_cpf_cnpj| caso                                   | mensagem_de_confirmacao_de_erro               |  mensagem                                         |          
      | web          | teste automatizado |        844.343.847-91    | 84434384791             |   para cadastro realizado com cpf      | Deseja realmente excluir este Fornecedor?     | O fornecedor foi removido do sistema com sucesso. |
      | web          | teste automatizado |        17.863.885/0001-55 | 17863885000155          |   para cadastro realizado com cnpj     | Deseja realmente excluir este Fornecedor?     | O fornecedor foi removido do sistema com sucesso. |
