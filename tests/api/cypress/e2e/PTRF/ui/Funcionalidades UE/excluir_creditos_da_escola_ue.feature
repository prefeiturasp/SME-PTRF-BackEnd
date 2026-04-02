# language: pt

Funcionalidade: Excluir créditos da escola

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar: <caso>
    Quando clico na opção Créditos da escola
    E clico em deletar no crédito da escola
    Então sistema exclue créditos da UE

    Exemplos:
      | visualizacao | caso                             |
      | web          | Exclusão do crédito              |
      | web          | Não permitir com período fechado |
      | web          | Cancela exclusão do crédito      |



