# language: pt
Funcionalidade: Cadastro Motivo de pagamento antecipado

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Cenário: Validar cadastro de motivo de pagamento antecipado com sucesso
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API
    E clico na opcao "Motivos Pagamento Antecipado"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "teste automatizado" da tela Motivo pagamento antecipado
    E clico no botao "Salvar" da tela Motivo pagamento antecipado
    Quando sistema apresenta a 'O motivo de pagamento antecipado foi adicionado ao sistema com sucesso.' na tela
    Entao excluo e confirmo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API

  Cenário: Validar cadastro de motivo de pagamento antecipado com nome em branco
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API
    E clico na opcao "Motivos Pagamento Antecipado"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "" da tela Motivo pagamento antecipado
    E clico no botao "Salvar" da tela Motivo pagamento antecipado
    Quando sistema apresenta a 'Nome do motivo é obrigatório' na tela
    Entao confirmo que o Motivo pagamento antecipado com o nome de motivo "teste automatizado" não existe via API

  Esquema do Cenário: Validar cadastro de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API
    E crio o Motivo pagamento antecipado com o nome de motivo 'teste automatizado' via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E clico no botao "Adicionar motivo de pagamento antecipado" da tela Motivo pagamento antecipado
    E informo dado nos campos "<nome_do_motivo_pagamento_antecipado>" da tela Motivo pagamento antecipado
    E clico no botao "Salvar" da tela Motivo pagamento antecipado
    Quando sistema apresenta a '<mensagem>' na tela
    E confirmo que existe exatamente um Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API
    Entao excluo e confirmo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" via API

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | nome_do_motivo_pagamento_antecipado | mensagem                                                                | caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                  | Este motivo de pagamento antecipado já existe.                          | com motivo duplicado         |
