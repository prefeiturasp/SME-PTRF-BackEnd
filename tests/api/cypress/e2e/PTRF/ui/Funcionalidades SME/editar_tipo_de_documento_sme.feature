# language: pt
Funcionalidade: Editar tipo de documento

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar edição de tipo de documento :<caso>
    E excluo o tipo de documento com o nome de "teste automatizado editado" via API
    E excluo o tipo de documento com o nome de "teste automatizado" via API
    E crio o tipo de documento com o nome de "teste automatizado" via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de documento
    E clico no botao "Filtrar" da tela tipo de documento
    E clico no botao "Editar" da tela tipo de documento
    E informo dado nos campos "<nome_tipo_do_documento>", "<solicitar_a_digitacao_do_numero_do_documento>","<no_numero_do_documento_deve_constar_apenas_digitos>","<documento_comprobatorio_de_despesa>","<habilita_preenchimento_do_imposto>", e "<documento_relativo_ao_imposto_recolhido>"  da tela tipo de documento
    E clico no botao "Salvar" da tela tipo de documento
    Quando sistema apresenta a '<mensagem>' na tela
    E confirmo que existe exatamente um tipo de documento com o nome de "<tipo_preservado>" via API
    E confirmo que o tipo de documento com o nome de "<tipo_ausente>" não existe via API
    Entao excluo e confirmo o tipo de documento com o nome de "<tipo_preservado>" via API

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome       | nome_tipo_do_documento        | solicitar_a_digitacao_do_numero_do_documento  | no_numero_do_documento_deve_constar_apenas_digitos  | documento_comprobatorio_de_despesa  | habilita_preenchimento_do_imposto  | documento_relativo_ao_imposto_recolhido  | mensagem                                                    | caso               | tipo_preservado            | tipo_ausente                |
      | web          | Tipos de Documento          | teste automatizado     | teste automatizado editado    | true                                          | false                                               | true                                 | true                              | false                                    | O tipo de documento foi editado no sistema com sucesso.     | com sucesso        | teste automatizado editado | teste automatizado          |
      | web          | Tipos de Documento          | teste automatizado     |                               | true                                          | false                                               | true                                 | true                              | false                                    | Nome é obrigatório                                          | com nome em branco | teste automatizado         | teste automatizado editado  |
