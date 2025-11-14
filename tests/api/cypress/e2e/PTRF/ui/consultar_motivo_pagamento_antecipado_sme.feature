# language: pt
Funcionalidade: Consultar Motivo de pagamento antecipado

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar pesquisa de motivo de pagamento antecipado :<caso>
    E excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados
    E crio o Motivo pagamento antecipado com o nome de motivo 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_motivo_de_pagamento_antecipado>" da tela de pesquisa de Motivo pagamento antecipado
    E clico no botao "Filtrar" da tela Motivo pagamento antecipado
    # Quando sistema retorna dados da consulta com os valores "<resutado_consulta>" na de pesquisa
    # Entao excluo o Motivo pagamento antecipado com o nome de motivo "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao  | filtrar_por_motivo_de_pagamento_antecipado |resutado_consulta           |caso                         |
      | web          | Motivos Pagamento Antecipado | teste automatizado                         |teste automatizado          |com sucesso                  |
      | web          | Motivos Pagamento Antecipado | automatizado                               |teste automatizado          |com nome parcial informado   |
      | web          | Motivos Pagamento Antecipado | dhasidgasiudgiausiduas                     |Nenhum resultado encontrado.|com nome inexistente na base |