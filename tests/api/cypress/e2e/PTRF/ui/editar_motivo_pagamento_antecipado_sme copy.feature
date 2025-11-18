# language: pt
Funcionalidade: Editar Motivo de pagamento antecipado

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar edição de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado editado" do banco de dados
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados
    E crio o Motivo pagamento antecipado com o nome de motivo 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_motivo_de_pagamento_antecipado>" da tela de pesquisa de Motivo pagamento antecipado
    E clico no botao "Filtrar" da tela Motivo pagamento antecipado
    # E clico no botao "Editar" da tela Motivo pagamento antecipado
    # E informo dado nos campos "<nome_do_motivo_pagamento_antecipado>" da tela Motivo pagamento antecipado
    # E clico no botao "Salvar" da tela Motivo pagamento antecipado
    # Quando sistema apresenta a '<mensagem>' na tela
    # Entao excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado editado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | filtrar_por_motivo_de_pagamento_antecipado |nome_do_motivo_pagamento_antecipado|mensagem                                                                    |caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                         |teste automatizado editado         |O motivo de pagamento antecipado foi editado no sistema com sucesso.        |com sucesso                  |
      | web          | Motivos Pagamento Antecipado | teste automatizado                         |                                   | Nome do motivo é obrigatório                                               |com nome em branco           |