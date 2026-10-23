# language: pt
Funcionalidade: Pesquisa tipo de documento

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar pesquisa de tipo de documento :<caso>
    E excluo o tipo de documento com o nome de "teste automatizado" via API
    E crio o tipo de documento com o nome de "teste automatizado" via API
    E clico na opcao "<opcao_painel_parametrizacao>"
    E informo dado nos campos "<filtrar_por_nome>" da tela tipo de documento
    E clico no botao "Filtrar" da tela tipo de documento
    Quando sistema retorna dados da consulta com os valores "<resutado_consulta>" na de pesquisa
    Entao excluo e confirmo o tipo de documento com o nome de "teste automatizado" via API

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | filtrar_por_nome       | resutado_consulta             | caso                         |
      | web          | Tipos de Documento          | dgytasgddaysdgysgd     | Nenhum resultado encontrado. | com nome inexistente na base |
