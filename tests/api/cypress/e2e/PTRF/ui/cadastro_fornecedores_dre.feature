# language: pt
Funcionalidade: Cadastro fornecedor

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "DRE"

  Esquema do Cenário: Validar cadastro de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado" do banco de dados
    E clico na opcao "Fornecedores" com a visao SME
    E clico no botao "Adicionar fornecedor" da tela Fornecedores
    E informo dado nos campos "<nome_do_fornecedor>" e "<cpf_cnpj>"
    E clico no botao "Salvar" da tela tipo de conta
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o fornecedor com o nome "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | nome_do_fornecedor | cpf_cnpj           | mensagem                                            | caso                             |
      | web          |                    |     88952264000196 | Nome é obrigatório                                  | com nome do fornecedor em branco |
      | web          | teste automatizado |                    | CPF / CNPJ é obrigatório                            | com CPF / CNPJ em branco         |
      | web          | teste automatizado |     111.111.111-11 | Digite um CPF / CNPJ válido                         | com CPF invalido                 |
      | web          | teste automatizado |      111.111.111-1 | Digite um CPF / CNPJ válido                         | com CPF incompleto               |
      | web          | teste automatizado | 11.111.111/1111-11 | Digite um CPF / CNPJ válido                         | com CNPJ invalido                |
      | web          | teste automatizado |  11.111.111/1111-1 | Digite um CPF / CNPJ válido                         | com CNPJ incompleto              |

  Esquema do Cenário: Validar cadastro de fornecedor :<caso>
    E excluo o fornecedor com o nome "teste automatizado" do banco de dados
    E crio o fornecedor com o nome 'teste automatizado' e "<cpf_cnpj>" no banco de dados
    E clico na opcao "Fornecedores" com a visao SME
    E clico no botao "Adicionar fornecedor" da tela Fornecedores
    E informo dado nos campos "<nome_do_fornecedor>" e "<cpf_cnpj>"
    E clico no botao "Salvar" da tela tipo de conta
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o fornecedor com o nome "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | nome_do_fornecedor | cpf_cnpj          | mensagem                                            | caso                     |
      | web          | teste automatizado | 45058821443       | Fornecedor com este CPF / CNPJ já existe.           | com registro duplicado   |
