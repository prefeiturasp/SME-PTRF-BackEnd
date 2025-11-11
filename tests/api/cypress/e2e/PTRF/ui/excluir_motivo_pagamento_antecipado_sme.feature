# language: pt
Funcionalidade: Excluir Motivo de pagamento antecipado

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar exclusão de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados
    E crio o Motivo pagamento antecipado com o nome de motivo 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_motivo_de_pagamento_antecipado>" da tela de pesquisa de Motivo pagamento antecipado
    E clico no botao "Filtrar" da tela Motivo pagamento antecipado
    E clico no botao "Editar" da tela Motivo pagamento antecipado
    E clico no botao "Apagar" da tela Motivo pagamento antecipado
    Quando clico no botao "Excluir" da tela Motivo pagamento antecipado
    Entao sistema apresenta a '<mensagem>' na tela

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | filtrar_por_motivo_de_pagamento_antecipado |mensagem                                                                    |caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                         |O motivo de pagamento antecipado foi removido do sistema com sucesso.       |com sucesso                  |