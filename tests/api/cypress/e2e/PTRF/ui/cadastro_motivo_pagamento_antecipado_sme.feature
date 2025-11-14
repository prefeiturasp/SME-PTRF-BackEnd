# language: pt
Funcionalidade: Cadastro Motivo de pagamento antecipado

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar cadastro de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "<nome_do_motivo_pagamento_antecipado>" da tela Motivo pagamento antecipado
    E clico no botao "Salvar" da tela Motivo pagamento antecipado
    # Quando sistema apresenta a '<mensagem>' na tela
    # Entao excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | nome_do_motivo_pagamento_antecipado | mensagem                                                                | caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                  | O motivo de pagamento antecipado foi adicionado ao sistema com sucesso. | com sucesso                  |
      | web          | Motivos Pagamento Antecipado |                                     | Nome do motivo é obrigatório                                            | com nome do motivo em branco |

  Esquema do Cenário: Validar cadastro de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados
    E crio o Motivo pagamento antecipado com o nome de motivo 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "<nome_do_motivo_pagamento_antecipado>" da tela Motivo pagamento antecipado
    E clico no botao "Salvar" da tela Motivo pagamento antecipado
    # Quando sistema apresenta a '<mensagem>' na tela
    # Entao excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | nome_do_motivo_pagamento_antecipado | mensagem                                                                | caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                  | Este motivo de pagamento antecipado já existe.                          | com motivo duplicado         |