# language: pt
Funcionalidade: Editar tipo de transação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar edição de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E crio o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de transacao
    E clico no botao "Filtrar" da tela tipos de transacao
    # E clico no botao "Editar" da tela tipos de transacao
    # E informo dado nos campos "<nome_tipo_de_transacao>" e "<tem_documento>" da tela tipo de transacao
    # E clico no botao "Salvar" da tela tipos de transacao
    # Quando sistema apresenta a '<mensagem>' na tela
    # Entao excluo o tipo de transacao com o nome de "teste editado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome        | nome_tipo_de_transacao | tem_documento  |mensagem                                                        | caso                               |
      | web          | Tipos de Transação          | teste automatizado      | teste editado          | false          |O tipo de transação foi editado no sistema com sucesso.         |com sucesso                         |
      | web          | Tipos de Transação          | teste automatizado      |                        | true           |Nome é obrigatório                                              |com nome em branco                  |
