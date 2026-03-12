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

  Cenário: Carregar painel de ações de associações
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no painel de ações de associações
    Então carrega o painel de ações de associações com status 200
  
  Cenário: Não carregar painel de ações sem associações
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no painel de ações sem associações
    Então não carrega o painel de ações de associações com status 404

  Cenário: Não carregar painel de ações de associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint no painel de ações de associações
    Então não carrega o painel de ações de associações retornando o status 401

  Cenário: Status de período de associações não encontrado
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no período de status de associações
    Então retorna status de período de associações não encontrado
  
  Cenário: Status de período de associações deve conter data
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no período de status sem data
    Então retorna que status de período de associações deve conter data

  Cenário: Não retornar status de período de associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no período de status de associações
    Então não carrega status de período de associações retornando o status 401

  Cenário: Buscar dados da tabela de associações
    Dado que possuo um token de acesso
    Quando envio uma requisição GET no endpoint na tabela associações
    Então retorna todos dados da tabela de associações com status 200
  
  Cenário: Não buscar dados da tabela de associações sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET no endpoint na tabela associações
    Então não busca dados da tabela de associações retornando o status 401

  Cenário: Consultar status da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET de consulta da associação
    Então retorna o status da associação com 200 no response

  Cenário: Não consulta status sem a associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET de consulta sem a associação
    Então não consulta o status sem a associação
  
  Cenário: Não consulta status da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET de consulta da associação
    Então não retorna o status da associação somente 401 no response

  Cenário: Consultar tags de informações da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET nas tags de informações
    Então retorna tags de informações da associação com status 200
  
  Cenário: Não consulta tags de informações da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET nas tags de informações
    Então não retorna tags de informações da associação com status 401

  Cenário: Verificação de regularidade da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET na verificação de regularidade
    Então retorna a verificação de regularidade da associação com status 200

  Cenário: Não consulta verificação de regularidade sem a associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET na verificação de regularidade sem associação
    Então não consulta a verificação de regularidade sem a associação
  
  Cenário: Não consulta verificação de regularidade da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET na verificação de regularidade
    Então não retorna a verificação de regularidade da associação

  Cenário: Retorna períodos para prestação de contas da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET nas contas da associação
    Então retorna períodos para prestação de contas da associação com status 200

  Cenário: Não retorna períodos para prestação de contas sem a associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET nas contas sem associação
    Então não consulta períodos para prestação de contas sem a associação
  
  Cenário: Não retorna períodos para prestação de contas da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET nas contas da associação
    Então não retorna períodos para prestação de contas da associação

  Cenário: Retorna contas encerradas da associação
    Dado que possuo um token de acesso
    Quando envio uma requisição GET em contas encerradas da associação
    Então retorna contas encerradas da associação com status 200

  Cenário: Não retorna contas encerradas sem a associação
    Dado que possuo um token de acesso
    Quando envio a requisição GET em contas encerradas sem associação
    Então não consulta contas encerradas sem a associação
  
  Cenário: Não retorna contas encerradas da associação sem autenticação
    Dado que não possuo um token de acesso
    Quando tento uma requisição GET em contas encerradas da associação
    Então não retorna contas encerradas da associação sem autenticação