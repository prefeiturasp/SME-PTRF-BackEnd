# language: pt
Funcionalidade: Editar tipo de transação

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar edição de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste editado" via API
    E excluo o tipo de transacao com o nome de "teste automatizado" via API
    E crio o tipo de transacao com o nome de "teste automatizado" via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de transacao
    E clico no botao "Filtrar" da tela tipos de transacao
    E clico no botao "Editar" da tela tipos de transacao
    E informo dado nos campos "<nome_tipo_de_transacao>" e "<tem_documento>" da tela tipo de transacao
    E clico no botao "Salvar" da tela tipos de transacao
    Quando sistema apresenta a '<mensagem>' na tela
    E confirmo que existe exatamente um tipo de transacao com o nome de "<tipo_preservado>" via API
    E confirmo que o tipo de transacao com o nome de "<tipo_ausente>" nao existe via API
    Entao excluo e confirmo o tipo de transacao com o nome de "<tipo_preservado>" via API

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome        | nome_tipo_de_transacao | tem_documento  |mensagem                                                        | caso                               | tipo_preservado    | tipo_ausente       |
      | web          | Tipos de Transação          | teste automatizado      | teste editado          | false          |O tipo de transação foi editado no sistema com sucesso.         |com sucesso                         | teste editado      | teste automatizado |
      | web          | Tipos de Transação          | teste automatizado      |                        | true           |Nome é obrigatório                                              |com nome em branco                  | teste automatizado | teste editado      |
