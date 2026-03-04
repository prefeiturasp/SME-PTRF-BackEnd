# language: pt

Funcionalidade: API - Associações 

  Cenário: Buscar dados das associações
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de associações
    Então retorna todos dados das associações com status 200
  
  Cenário: Não buscar dados das associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint de associações
    Então não busca dados das associações retornando o status 401

  Cenário: Buscar dados da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint da associação
    Então retorna todos dados da associação com status 200
  
  Cenário: Não buscar dados da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint da associação
    Então não busca dados da associação retornando o status 401

  Cenário: Buscar as contas vinculadas
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint das contas da associação
    Então retorna todos as contas vinculadas com status 200
  
  Cenário: Não buscar as contas vinculadas sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint das contas da associação
    Então não busca as contas vinculadas retornando o status 401

  Cenário: Buscar as contas encerradas da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET nas contas encerradas
    Então retorna as contas encerradas da associação com status 200

  Cenário: Não buscar as contas encerradas sem associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET em contas encerradas
    Então não busca as contas encerradas sem associação
  
  Cenário: Não buscar as contas encerradas da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET nas contas encerradas
    Então não busca as contas encerradas da associação retornando o status 401
  
  Cenário: Exportar dados da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET para exportar associação
    Então exportar dados da associação com status 200

  Cenário: Não exportar dados da associação sem associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET de exportar sem associação
    Então não exportar dados da associação
  
  Cenário: Não exportar dados da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET para exportar associação
    Então não exportar dados da associação retornando o status 401

  Cenário: Exportar PDF de dados da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET para exportar PDF da associação
    Então exportar dados da associação em PDF com status 200

  Cenário: Não exportar PDF de dados da associação sem associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET de exportar PDF sem associação
    Então não exportar PDF de dados da associação
  
  Cenário: Não exportar PDF de dados da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET para exportar PDF da associação
    Então não exportar PDF de dados da associação retornando o status 401

  Cenário: Buscar associações no EOL
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint de associação EOL
    Então retornar dados da associação no EOL com status 200
  
  Cenário: Não buscar associações no EOL sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint de associação EOL
    Então não busca dados da associação no EOL com status 401