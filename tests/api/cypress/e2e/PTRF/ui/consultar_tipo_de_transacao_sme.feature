# language: pt
Funcionalidade: Pesquisa tipo de transação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar pesquisa de tipo de transação :<caso>
    E excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E crio o tipo de transacao com o nome de "teste automatizado" do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de transacao
    E clico no botao "Filtrar" da tela tipos de transacao
    # E sistema retorna dados da consulta com os valores "<resutado_consulta>" na de pesquisa
    # Quando sistema retorna dados da consulta com os valores "<valores_consulta>"
    # Entao excluo o tipo de transacao com o nome de "teste automatizado" do banco de dados

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome       | valores_consulta                     |resutado_consulta               | caso                                |
      | web          | Tipos de Transação          | teste automatizado     | Exibindo 1 tipo(s) de transação      | teste automatizado             | com sucesso                         |
      | web          | Tipos de Transação          |       automatizado     | Exibindo 1 tipo(s) de transação      | teste automatizado             | com nome parcial informado          |
      | web          | Tipos de Transação          | dgytasgddaysdgysgd     |                                      | Nenhum resultado encontrado.   | com nome inexistente na base        |