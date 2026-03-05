# language: pt

Funcionalidade: API - Contas associações 

  Cenário: Buscar as contas das associações 
    Dado que possuo um token de acesso
    Quando envio uma requisição GET na contas associações
    Então retorna dados das contas associações com status 200
  
  Cenário: Não buscar as contas das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET na contas associações
    Então não busca dados das contas associações retornando o status 401

  Cenário: Filtrar as contas das associações 
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no filtro na contas associações
    Então retorna filtrando dados das contas associações com status 200
  
  Cenário: Não filtra as contas das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento a requisição GET no filtro de contas associações
    Então não filtra dados das contas associações retornando o status 401

  Cenário: Buscar por id de conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição GET do id de conta das associações
    Então busca os dados das contas associações com status 200

  Cenário: Não buscar por id de conta das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento requisição GET do id de conta das associações
    Então não busca os dados das contas associações retornando o status 401

  Cenário: Alterar por id de conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT do id de conta das associações
    Então altera os dados das contas associações com status 200

  Cenário: Id da associação deve ser informado para alterar conta
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT sem id de conta das associações
    Então não altera os dados das contas associações com status 400
  
  Cenário: Id deve ser obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT sem id em conta das associações
    Então não altera os dados das contas associações com método inválido

  Cenário: Tipo de conta é obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT sem tipo em conta das associações
    Então não altera os dados das contas associações sem o tipo com status 400

  Cenário: Status é obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PUT sem status em conta das associações
    Então não altera os dados das contas associações sem status

  Cenário: Não altera por id de conta das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento requisição PUT do id de conta das associações
    Então não altera os dados das contas associações retornando o status 401

   Cenário: Atualizar por id de conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PATCH do id de conta das associações
    Então altera os dados das contas associações com status 200

  Cenário: Id da associação deve ser informado para atualizar conta
    Dado que possuo um token de acesso
    Quando envio uma requisição PATCH sem id de conta das associações
    Então não atualiza os dados das contas associações com status 400
  
  Cenário: Id deve ser obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PATCH sem id em conta das associações
    Então não atualiza os dados das contas associações com método inválido

  Cenário: Tipo de conta é obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PATCH sem tipo em conta das associações
    Então não atualiza os dados das contas associações sem o tipo com status 400

  Cenário: Status é obrigatório nas conta das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição PATCH sem status em conta das associações
    Então não atualiza os dados das contas associações sem status

  Cenário: Não altera por id de conta das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento requisição PATCH do id de conta das associações
    Então não atualiza os dados das contas associações retornando o status 401