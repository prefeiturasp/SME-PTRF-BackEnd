# language: pt
Funcionalidade: Excluir tipo de documento

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar exclusão de tipo de documento :<caso>
    E excluo o tipo de documento com o nome de "teste automatizado" do banco de dados
    E crio o tipo de documento com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de documento
    E clico no botao "Filtrar" da tela tipo de documento
    # E clico no botao "Editar" da tela tipo de documento
    # E clico no botao "Excluir" da tela tipo de documento
    # E sistema apresenta a '<mensagem_confirmacao_exclusao>' na tela
    # Quando clico no botao "Confirmar Excluir" da tela tipo de documento
    # Entao sistema apresenta a '<mensagem>' na tela

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome       | mensagem                                                           |mensagem_confirmacao_exclusao                         | caso                         |
      | web          | Tipos de Documento          | teste automatizado     | O tipo de documento foi removido do sistema com sucesso.           |Tem certeza que deseja excluir esse tipo de documento?| com sucesso                  |