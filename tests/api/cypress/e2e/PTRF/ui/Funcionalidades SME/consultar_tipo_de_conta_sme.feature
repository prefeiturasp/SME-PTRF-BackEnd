# language: pt
Funcionalidade: Consultar Tipo de Conta

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "SME"
  @ignore  
  Esquema do Cenário: Validar consulta de tipo conta:<caso>
    E excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    E crio o tipo conta com o nome 'teste automatizado' do banco de dados
    E clico na opcao "<opcao_painel_parametrizacao>" 
    E informo dados no campo '<dados_da_pesquisa>' da tela de tipo de conta
    E clico no botao "Pesquisar" da tela tipo de conta
    Quando sistema retorna dados da consulta com os valores "<valores_consulta>"
    Entao excluo o tipo conta com o nome 'teste automatizado' do banco de dados
    

    Exemplos:
      | visualizacao | opcao_painel_parametrizacao | dados_da_pesquisa         |valores_consulta          | caso                           |
      | web          | Tipo                        |   teste automatizado      |Exibindo 1 tipos de conta | com sucesso                    | 
      | web          | Tipo                        |   teste automatizadooooo  |Exibindo 0 tipos de conta | com dados inexistentes na base | 