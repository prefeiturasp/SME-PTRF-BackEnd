# language: pt
Funcionalidade: Editar fornecedor

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "DRE"

  Esquema do Cenário: Validar edição de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado editado" do banco de dados
    E excluo o fornecedor com o nome "teste automatizado" do banco de dados
    E crio o fornecedor com o nome 'teste automatizado' e "<valores_consulta_cpf_cnpj>" no banco de dados
    E clico na opcao "Fornecedores" com a visao SME
    E informo dado nos campos "<nome_do_fornecedor>" e "<cpf_cnpj>" para pesquisa na tela de Fornecedores
    E clico no botao "Filtrar" da tela Fornecedores
    # E clico no botao "Editar" da tela fornecedor na tabela com a opcao 'teste automatizado'
    # E informo dado nos campos "<nome_do_fornecedor_editado>" e "<cpf_cnpj_editado>"
    # E clico no botao "Salvar" da tela Fornecedores
    # Quando sistema apresenta a '<mensagem>' na tela
    # Entao excluo o fornecedor com o nome "teste automatizado editado" do banco de dados

    Exemplos:
      | visualizacao | nome_do_fornecedor | cpf_cnpj              |valores_consulta_cpf_cnpj|nome_do_fornecedor_editado  |cpf_cnpj_editado| mensagem                                          | caso                                   |        
      | web          | teste automatizado |        84434384791    | 84434384791             | teste automatizado editado | 51244772020    | O fornecedor foi editado no sistema com sucesso.  |   com cadastro cpf para cpf            |
      | web          | teste automatizado |        84434384791    | 84434384791             | teste automatizado editado | 22512581000183 | O fornecedor foi editado no sistema com sucesso.  |   com cadastro cpf para cnpj           |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado | 22512581000183 | O fornecedor foi editado no sistema com sucesso.  |   com cadastro cnpj para cnpj          |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado | 51244772020    | O fornecedor foi editado no sistema com sucesso.  |   com cadastro cnpj para cpf           |
      | web          | teste automatizado |        22512581000183 | 22512581000183          |                            | 51244772020    | Nome é obrigatório                                |   com nome em brancoo                  |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado |                | CPF / CNPJ é obrigatório                          |   com cpf/cnpj em branco               |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado |  5124477200    | Digite um CPF / CNPJ válido                       |   com cpf incompleto                   |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado |  51244772001   | Digite um CPF / CNPJ válido                       |   com cpf inexistente                  |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado |  2251258100018 | Digite um CPF / CNPJ válido                       |   com cnpj incompleto                  |
      | web          | teste automatizado |        22512581000183 | 22512581000183          | teste automatizado editado |  22512581000181| Digite um CPF / CNPJ válido                       |   com cnpj inexistente                 |