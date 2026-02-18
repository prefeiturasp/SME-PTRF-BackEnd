# language: pt
Funcionalidade: Editar dados da associação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar edição dos dados da associação: <caso>
    E informo "<nome_associacao>" e "<ccm>"
    Quando clico no botão "Salvar" 
    Então sistema retorna a "<mensagem>" 

    Exemplos:
      | visualizacao | nome_associacao                                   | ccm         | mensagem                        | caso                          |
      | web          | ASSOCIACAO DE PAIS E MESTRES DA EMEI AFONSO CELSO | 3.749.984-0 | A edição foi salva com sucesso! | Nome e CCM                    |
  
  Esquema do Cenário: Validar edição dos dados da associação: <caso>
    E informo "<nome_associacao>" e "<ccm>"
    Quando clico no botão "Salvar" 
    Então sistema retorna o "<alerta>" 

    Exemplos:
      | visualizacao | nome_associacao                                   | ccm         | alerta                        | caso                          |
      | web          |                                                   | 3.749.984-0 | Nome é obrigatório            | Não permitir campo nome vazio |

  Esquema do Cenário: Validar campos de leitura: <caso>
    Quando tento editar os campos de leitura
    Então não permite a edição

    Exemplos:
      | visualizacao | caso                   |
      | web          | Bloqueados para edição |

  Esquema do Cenário: Validar botão de cancelar: <caso>
    Quando clico no botão "Cancelar"
    Então retorna à visualização sem salvar alterações

    Exemplos:
      | visualizacao | caso                   |
      | web          | Cancelamento da edição |