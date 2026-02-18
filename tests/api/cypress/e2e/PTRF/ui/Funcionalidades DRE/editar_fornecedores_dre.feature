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
    E clico no botao "Editar" da tela fornecedor na tabela com a opcao 'testes automatizado'
    E informo dado nos campos "<nome_do_fornecedor_editado>" e "<cpf_cnpj_editado>"
    E clico no botao "Salvar" da tela Fornecedores
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o fornecedor com o nome "teste automatizado editado" do banco de dados

    Exemplos:
      | visualizacao | nome_do_fornecedor   | cpf_cnpj                  |valores_consulta_cpf_cnpj|nome_do_fornecedor_editado  |cpf_cnpj_editado| mensagem                                                | caso                                   |        
      | web          | testes automatizados |        17.863.885/0001-55 | 17863885000155          |                              | 22.512.581/0001-83 | Nome é obrigatório                                |   com nome em brancoo                  |
      | web          | testes automatizados |        17.863.885/0001-55 | 17863885000155          | testes automatizados editado |                | CPF / CNPJ é obrigatório                              |   com cpf/cnpj em branco               |
      | web          | testes automatizados |        17.863.885/0001-55 | 17863885000155          | testes automatizados editado |  5124477200    | Digite um CPF / CNPJ válido                           |   com cpf incompleto                   |
      | web          | testes automatizados |        17.863.885/0001-55 | 17863885000155          | testes automatizados editado |  51244772001   | Digite um CPF / CNPJ válido                           |   com cpf inexistente                  |
      | web          | testes automatizados |        17.863.885/0001-55 | 17863885000155          | testes automatizados editado |  2251258100018 | Digite um CPF / CNPJ válido                           |   com cnpj incompleto                  |
      | web          | testes automatizados |        17.863.885/0001-55 | 22512581000183          | teste automatizado editado   |  22512581000181| Digite um CPF / CNPJ válido                           |   com cnpj inexistente                 |