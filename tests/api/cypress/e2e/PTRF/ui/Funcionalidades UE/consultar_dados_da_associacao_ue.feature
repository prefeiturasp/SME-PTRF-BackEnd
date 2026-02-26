# language: pt
Funcionalidade: Consultar dados da associação

  Contexto:
    Dado eu acesso o sistema com a visualização "<visualizacao>"
    E realizo login no sistema PTRF com perfil "UE"

  Esquema do Cenário: Validar dados da associação: <caso>
    Quando clico na opção Dados da Associação
    Então sistema retorna "<valor_esperado>" para o campo "<campo>"

    Exemplos:
      | visualizacao | campo           | valor_esperado                                    | caso               |
      | web          | nome_associacao | ASSOCIACAO DE PAIS E MESTRES DA EMEI AFONSO CELSO | Nome da Associação |
      | web          | codigo_eol      | 092461                                            | Código EOL         |
      | web          | dre             | DIRETORIA REGIONAL DE EDUCACAO IPIRANGA           | Diretoria Regional |
      | web          | cnpj            | 52.442.969/0001-16                                | CNPJ               |
      | web          | ccm             | 3.749.984-0                                       | CCM                |
      | web          | email           | emeiafcelso@sme.prefeitura.sp.gov.br              | Email              |

  Esquema do Cenário: Validar exportação da associação: <caso>
    Quando clico para exportar "<botao>"
    Então sistema exporta os dados da associação

    Exemplos:
      | visualizacao | botao               | caso             |
      | web          | dados da associação | Dados exportados |
      | web          | ficha cadastral     | Ficha exportada  |
