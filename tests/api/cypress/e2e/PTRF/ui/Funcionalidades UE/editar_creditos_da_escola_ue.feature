# language: pt

Funcionalidade: Editar créditos da escola

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar: <caso>
    Quando clico na opção Créditos da escola
    E clico em editar no crédito da escola
    Então sistema altera os créditos da UE

    Exemplos:
      | visualizacao | caso                                  |
      | web          | Edição do crédito                     |
      | web          | Não permite edição no período fechado |
      | web          | Campos obrigatórios na edição         |
      | web          | Voltar a listagem                     |




