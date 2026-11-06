# language: pt
Funcionalidade: Consultar Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "web"
    E realizo login no sistema PTRF com perfil "SME"

  Esquema do Cenário: Validar consulta de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' via API
    E crio o tipo conta com o nome 'teste automatizado' via API
    E clico na opcao "<opcao_painel_parametrizacao>" 
    E informo dados no campo '<dados_da_pesquisa>' da tela de tipo de conta
    E clico no botao "Pesquisar" da tela tipo de conta
    Quando sistema retorna dados da consulta com os valores "<valores_consulta>"
    Entao excluo e confirmo o tipo conta com o nome 'teste automatizado' via API
    

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | dados_da_pesquisa         |valores_consulta          | caso                           |
      | web          | Tipo                        |   teste automatizado      |Exibindo 1 tipo(s) de conta(s) | com sucesso                    |
      | web          | Tipo                        |   teste automatizadooooo  |Exibindo 0 tipo(s) de conta(s) | com dados inexistentes na base |
