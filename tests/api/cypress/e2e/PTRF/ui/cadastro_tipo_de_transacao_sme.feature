# language: pt
Funcionalidade: Cadastro tipo de transação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar cadastro de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar tipo de transacao" da tela tipos de transacao
    E informo dado nos campos "<nome_tipo_de_transacao>" e "<tem_documento>" da tela tipo de transacao
    E clico no botao "Salvar" da tela tipos de transacao
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_tipo_de_transacao | tem_documento | mensagem                                                   | caso                                   |
      | web          | Tipos de Transação          |                        | false         | Nome é obrigatório                                         | com campo nome em branco.              |

  Esquema do Cenário: Validar cadastro de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E crio o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar tipo de transacao" da tela tipos de transacao
    E informo dado nos campos "<nome_tipo_de_transacao>" e "<tem_documento>" da tela tipo de transacao
    E clico no botao "Salvar" da tela tipos de transacao
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_tipo_de_transacao | tem_documento | mensagem                                                   | caso                                   |
      | web          | Tipos de Transação          | teste automatizado     | true          | Já existe um tipo de transação com esse nome               | com tipo transacao duplicada           |
