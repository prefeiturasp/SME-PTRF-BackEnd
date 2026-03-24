# language: pt

Funcionalidade: Cadastrar créditos da escola

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar campos obrigatórios: <caso>
    Quando clico na opção Créditos da escola
    E cadastro crédito da escola sem preencher os dados
    Então sistema não permite salvar créditos da UE

    Exemplos:
      | visualizacao | caso                |
      | web          | Não permitir salvar |

  Esquema do Cenário: Validar exibição do: <caso>
    Quando clico na opção Créditos da escola
    E cadastro "<campo>" como crédito da escola
    Então sistema insere "<campo>" nos créditos da UE

    Exemplos:
      | visualizacao | campo           | caso                 |
      | web          | Recurso Externo | Cadastrar recurso    |
      | web          | Rendimento | Cadastrar rendimento |
      | web          | Repasse | Cadastrar repasse |
