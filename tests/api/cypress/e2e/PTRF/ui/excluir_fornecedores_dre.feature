# language: pt
Funcionalidade: Excluir fornecedor

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "DRE"

  Esquema do Cenário: Validar exclusão de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado" do banco de dados
    E crio o fornecedor com o nome 'teste automatizado' e "<valores_consulta_cpf_cnpj>" no banco de dados
    E clico na opcao "Fornecedores" com a visao SME
    E informo dado nos campos "<nome_do_fornecedor>" e "<cpf_cnpj>" para pesquisa na tela de Fornecedores
    E clico no botao "Filtrar" da tela Fornecedores
    E clico no botao "Editar" da tela fornecedor na tabela com a opcao 'teste automatizado'
    E clico no botao "Apagar" da tela Fornecedores
    E sistema apresenta a "<mensagem_de_confirmacao_de_erro>" para afirmacao da exclusao
    Quando clico no botao "Excluir" da tela Fornecedores
    Entao sistema apresenta a '<mensagem>' na tela

    Exemplos:
      | visualizacao | nome_do_fornecedor | cpf_cnpj              |valores_consulta_cpf_cnpj| caso                                   | mensagem_de_confirmacao_de_erro               |  mensagem                                         |          
      | web          | teste automatizado |        84434384791    | 84434384791             |   para cadastro realizado com cpf      | Deseja realmente excluir este Fornecedor?     | O fornecedor foi removido do sistema com sucesso. |
      | web          | teste automatizado |        17863885000155 | 17863885000155          |   para cadastro realizado com cnpj     | Deseja realmente excluir este Fornecedor?     | O fornecedor foi removido do sistema com sucesso. |