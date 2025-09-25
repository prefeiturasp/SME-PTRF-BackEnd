# language: pt
Funcionalidade: consultar fornecedor

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "DRE"

  Esquema do Cenário: Validar pesquisa de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado" do banco de dados
    E crio o fornecedor com o nome 'teste automatizado' e "<cpf_cnpj>" no banco de dados
    E clico na opcao "Fornecedores" com a visao SME
    E informo dado nos campos "<nome_do_fornecedor>" e "<valores_consulta_cpf_cnpj>" para pesquisa na tela de Fornecedores
    E clico no botao "Filtrar" da tela Fornecedores
    Quando sistema retorna dados da consulta com os valores "<valores_consulta_nome_fornecedor>" e "<valores_consulta_cpf_cnpj>" na tela de Fornecedores
    Entao excluo o fornecedor com o nome "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | nome_do_fornecedor   | cpf_cnpj              |valores_consulta_nome_fornecedor |valores_consulta_cpf_cnpj| caso                                                     |
      | web          | testes automatizados |     84434384791       | testes automatizados              | 844.343.847-91          |   informando dados em todos os campos com valor cpf      |
      | web          | testes automatizados |  17863885000155       | testes automatizados              | 17.863.885/0001-55      |   informando dados em todos os campos com valor cnpj     |
      | web          |                      |  17863885000155       | testes automatizados              | 17.863.885/0001-55      |   informando dados somente no campo de cnpj              |
      | web          |                      |     84434384791       | testes automatizados              | 844.343.847-91          |   informando dados somente no campo de cpf               |
      | web          | testes automatizados |     84434384791       | testes automatizados              |                         |   informando dados somente no campo de nome              |
