# language: pt
Funcionalidade: Cadastro tipo de documento

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar cadastro de tipo de documento :<caso>
    E excluo o tipo de documento com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "<nome_tipo_do_documento>", "<solicitar_a_digitacao_do_numero_do_documento>","<no_numero_do_documento_deve_constar_apenas_digitos>","<documento_comprobatorio_de_despesa>","<habilita_preenchimento_do_imposto>", e "<documento_relativo_ao_imposto_recolhido>"  da tela tipo de documento
    E clico no botao "Salvar" da tela tipo de documento
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo de documento com o nome de "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_tipo_do_documento | solicitar_a_digitacao_do_numero_do_documento | no_numero_do_documento_deve_constar_apenas_digitos | documento_comprobatorio_de_despesa | habilita_preenchimento_do_imposto | documento_relativo_ao_imposto_recolhido | mensagem                                                   | caso                     |
      | web          | Tipos de Documento          | teste automatizado     | true                                         | true                                               | true                               | true                              | true                                    | O tipo de documento foi adicionado ao sistema com sucesso. | com sucesso              |
      | web          | Tipos de Documento          |                        | true                                         | true                                               | true                               | true                              | true                                    | Nome é obrigatório                                         | com campo nome em branco |

  Esquema do Cenário: Validar cadastro de tipo de documento :<caso>
    E excluo o tipo de documento com o nome de "teste automatizado" do banco de dados
    E crio o tipo de documento com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "<nome_tipo_do_documento>", "<solicitar_a_digitacao_do_numero_do_documento>","<no_numero_do_documento_deve_constar_apenas_digitos>","<documento_comprobatorio_de_despesa>","<habilita_preenchimento_do_imposto>", e "<documento_relativo_ao_imposto_recolhido>"  da tela tipo de documento
    E clico no botao "Salvar" da tela tipo de documento
    Quando sistema apresenta a '<mensagem>' na tela
    Entao excluo o tipo de documento com o nome de "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | nome_tipo_do_documento | solicitar_a_digitacao_do_numero_do_documento | no_numero_do_documento_deve_constar_apenas_digitos | documento_comprobatorio_de_despesa | habilita_preenchimento_do_imposto | documento_relativo_ao_imposto_recolhido | mensagem                          | caso                          |
      | web          | Tipos de Documento          | teste automatizado     | true                                         | true                                               | true                               | true                              | true                                    | Este tipo de documento já existe. | com tipo documento duplicado  |
