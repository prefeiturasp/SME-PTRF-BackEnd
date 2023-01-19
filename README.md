# SME-PTRF-BackEnd
========

API da aplicação *SIG.Escola* da Secretaria de Educação da cidade de São Paulo.

License: MIT

Versão: 6.0.0

## Release Notes

### 6.0.0 - 19/01/2023 - Entregas da Release 6 - (Sprints 48 a 58)
* UE > Análise da DRE: Acertos: Detalhes de realização para acertos conforme a categoria
* UE > Novo Relatório de apresentação de PC após acertos
* UE > Prestações de Contas: Geração de Documentos: Documentos prévias/finas de devolução são gerados apenas nos casos que solicitações requerem mudanças
* UE > Prestações de Contas: Atas de apresentação e retificação agora são bloqueadas para alteração após recebimento pela DRE
* UE > O status do período agora inclui informação do status da PC mesmo quando o período ainda está em andamento
* UE > Conciliação Bancária: Nova opção Voltar que retorne para a tela anterior
* UE / DRE > Análise DRE: Relatório de acertos alterações de layout
* UE / DRE  > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Edição do lançamento" em Créditos
* UE / DRE  > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Exclusão do lançamento", em Gastos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Exclusão do lançamento", em Créditos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Devolução ao tesouro" em lançamentos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Ajustes externos", em Lançamentos e Documentos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Solicitação de esclarecimento" em lançamentos e documentos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Inclusão de gasto" em documentos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Edição do lançamento" em Créditos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Exclusão do lançamento", em Gastos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria "Exclusão do lançamento", em Créditos
* UE / DRE > Reabertura Seletiva do Período. Detalhes de realização para acertos de categoria   "Inclusão de crédito" em documentos
* UE / DRE > INATIVAÇÃO - Agora os créditos e despesas tem a opção de inativação e todos as operações realizadas levam em consideração essa inativação.
* DRE > Acompanhamento de PC: Devolução de PC: Agora apaga fechamentos e docs apenas se necessário
* DRE > Acompanhamento de PC: Solicitação de acertos agora agrupa os tipos de acerto na seção e apresenta informações se a solicitação acarretará ou não mudanças em lançamentos financeiros
* DRE > Acompanhamento de PC: Solicitações de devolução ao tesouro agora exigem todos os campos
* DRE > Acompanhamento de PC: Conferência de Documentos: Nova opção de marcar como corretos para documentos com solicitações de ajuste
* DRE > Acompanhamento de PC: Ver resumo: Alterações de nomenclatura das opções
* DRE > Relatório Consolidado: Agora é gerada Lauda Única com todas as contas
* DRE > Relatório Consolidado: Alterações na exibição do valor de Devolução ao Tesouro no Demonstrativo 
* SME > Parametrizações: Tipos de acertos em lançamentos: Novo card e Cadastro
* SME > Parametrizações: Tipos de acertos em Documentos: Novo Card e Cadastro
* GLO > 🐞 Correção de bugs.

### 1.33.0 - 24/08/2022 - Entregas da Release 5 - (Sprints 43 a 47)
* UE  > Na emissão da ata, agora a aplicação informa quais campos estão incompletos.
* UE  > Novo fluxo de informação de valores reprogramados iniciais. 
* DRE > Novo fluxo de aprovação de valores reprogramados iniciais.
* DRE > Novo processo de geração de relatórios consolidados, agora é possível gerações parciais.
* DRE > Após completar as gerações parciais de um relatório consolidado, é possível gerar uma versão unificada com todas as parciais. 
* DRE > Relatório de Execução Físico-Financeira agora é único para todas as contas.
* DRE > Nova consulta em tela do relatório de Execução Físico-Financeira, agora em uma versão mais simplificada e com todas as contas em uma mesma tela.
* DRE > Ata de parecer técnico não exibe mais valores financeiros e agrupa as PCs apenas por status, não mais por conta.
* DRE > Melhorias na conferência de lançamentos do acompanhamento de PC: Tags de informações e novos filtros.
* DRE > Mudanças no layout da lauda.
* DRE > No acompanhamento de PCs, as PCs que constam em relatórios consolidados não podem mais voltar para análise.
* DRE > Nova funcionalidade de Acesso de Suporte às unidades educacionais.
* SME > Nova funcionalidade de Acesso de Suporte às diretorias e unidades educacionais.
* SME > Nova central de extração de dados.
* SME > Extração de dados de créditos.
* ADM > Ação a partir de comissões para definição da comissão de exame de contas.
* ADM > Novos filtros em tipos de acertos em lançamentos.
* ADM > Novos filtros em tipos de acertos em documentos.
* ADM > Registro de movimentações nos arquivos de análise de PCs para fins de auditoria.
* GLO > Formulário de login agora exibe informação sobre o critério de senha diferente das anteriores.
* GLO > A redefinição de Senha agora exibe informação sobre o critério de senha diferente das anteriores.
* GLO > Incluída a informação de hora de criação no rodapé de vários relatórios.
* GLO > 🐞 Correção de bugs.

### 1.32.0 - 01/06/2022 - Entregas da Release 4c - Sprint 42
* DRE > Exibição do período e remoção do histórico de devoluções em análise de PC
* DRE > Remoção do bloco "Cobrança da PC" e revisão do bloco "Comentários" em análise de PC
* DRE > Substituição do formato do relatório de Demonstrativo da execução físico-financeira de Excel para PDF
* DRE > Melhorias na ata de parecer técnico em PDF
* DRE > Melhorias na ata de parecer técnico em tela
* DRE > Implementada ação para retirar atribuições em atribuições por unidade
* Melhorias na área de administração do sistema
* 🐞 Correção de bugs

### 1.31.0 - 16/05/2022 - Entregas da Release 4b - Sprint 41
* DRE > Novos filtros na confêrencia de lançamentos na análise de PC
* DRE > Solicitação de ajustes de saldo bancário em análise de PC
* DRE > Exibição de data da transação no estorno em análise de PC 
* DRE > Exibição de informações de ajustes de saldo bancário em resumo de acertos
* DRE > Melhorias no relatório de acertos em PDF
* DRE > Melhorias na ata de parecer técnico em PDF
* 🐞 Correção de bugs

### 1.30.0 - 02/05/2022 - Entregas da Release 4 - Sprint 40
* UE > Melhorias no cadastro e edição de presentes da ata de prestação de contas
* UE > Melhorias no demonstrativo financeiro
* UE > No cadastro de membros, agora é possível selecionar o cargo quando o servidor tiver mais de um
* UE > Exibição de informações de retenção de imposto nos gastos da escola
* DRE > Exibição de informações de retenção de imposto na análise de PC
* 🐞 Correção de bugs 

### 1.29.0 - 25/04/2022 - Entregas da Release 3 - Sprints 37 a 39
* UE > Implementado o registro de justificativas de pagamentos antecipados
* UE > Implementado o recurso de retenção de impostos nas despesas
* UE > Aprimorado o cadastro de despesas sem comprovação fiscal
* UE > Agora os estornos pedem a informação dos motivos de estorno
* UE > A app agora considera o período de conciliação para determinar se uma despesa está ou não demonstrada
* Melhorias visuais diversas
* 🐞 Correção de bugs 

### 1.28.0 - 03/03/2022 - Entregas da Sprint 36
* UE > Implementada funcionalidade de estorno de gastos
* UE > O demonstrativo financeiro passa a exibir informações de estornos
* DRE > O Acompanhamento de PC passa a exibir informações de estorno
* DRE > O status de PC "Retornada após acertos" passa a chamar "Apresentada após acertos"
* 🐞 Correção de bugs

### 1.27.0 - 22/02/2022 - Entregas da Sprint 35
* UE > Notificações de reprovação agora informam ou não os motivos dependendo das permissões do destinatário
* UE > Ata de apresentação passa a pedir e exibir justificativa para a existência de repasses pendentes
* UE e DRE > Consulta de resumo de acertos passa a exibir informação de data de retorno de devolução
* UE > Verificação de saldo no momento de lançamento de despesa agora considera saldos anteriores mesmo de períodos abertos
* DRE > Inclusão de campo para informação de recomendações ao aprovar uma PC com ressalvas
* 🐞 Correção de bugs

### 1.26.0 - 07/02/2022 - Entregas da Sprint 34
* UE > A conciliação bancária agora só trada de gastos; créditos são conciliados automaticamente 
* UE > Várias mudanças na forma que a conciliação bancária trata transações de períodos anteriores
* UE > Algumas mudanças de layout na conciliação bancária
* UE > Notificações de comentários agora são recebidos por qualquer usuário com a permissão 
* UE > Agora é possível gerar prévias de atas de apresentação e retificação antes de concluir o período
* UE > O formulário de devoluções ao tesouro na ata de retificação foi simplificado
* UE > Foram feitas várias mudanças de textos nas atas de apresentação e retificação de PC
* UE > Agora no Demonstrativo Financeiro em PDF não ocorre mais quebra de página no meio de uma ação no bloco 3
* DRE > Implementada a ata de parecer técnico em tela e PDF
* DRE > Implementada a geração das laudas de parecer técnico
* DRE > Em Dados da Diretória não é mais obrigatório a digitação do CNPJ
* DRE > Melhoria na distribuição das colunas na análise de lançamentos de uma PC
* DRE > Agora o dashboard de acompanhamento de PCs chama a atenção para a existência de PCs apresentadas
* DRE > Agora a análise de prestações de contas mantém o último estado de seleções e posição para facilitar o uso
* ADM > Agora é possível desativar o envio de e-mails em notificações
* Ajustes de textos diversos
* 🐞 Correção de bugs


### 1.25.0 - 29/12/2021 - Entregas da Sprint 33
* UE > Atas de apresentação e retificação agora incluem o horário da reunião
* DRE > Resumo de acertos em tela agora exibe as solicitações de ajustes de valores reprogramados
* DRE > Resumo de acertos em PDF agora exibe as solicitações de ajustes de valores reprogramados
* DRE > Melhorias na navegabilidade do acompanhamento de PCs
* DRE > Novo módulo de lançamento e consulta de análises de regularidade das associações
* DRE > Novo módulo de cadastro de comissões
* ADM > Implementado parametrização de quais aplicações são aceitas por cada ação
* 🐞 Correção de bugs

### 1.24.0 - 02/12/2021 - Entregas da Sprint 32 (Complemento)
* UE > Atas de apresentação e retificação agora trazem a lista de presença de membros em ordem de cargo
* UE > Atas de apresentação e retificação agora trazem a lista de presença de não membros em ordem alfabética
* UE > Agora o campo número de documento em Despesas só aceita dígitos.
* DRE > O resumo de acertos passa a só exibir a aba "Conferência Atual" em PCs em análise 
* DRE > Implementado a solicitação de ajustes em valores reprogramados de períodos iniciais
* DRE > Alterada a consulta de resumo de acertos para exibir ajustes em valores reprogramados de períodos iniciais
* DRE > Alterado o relatório de devolução para acertos para exibir ajustes em valores reprogramados de períodos iniciais
* ADM > Agora é possível inativar um usuário temporariamente sem ter que alterar seus grupos de acesso
* Agora sub-menus sem itens visíveis são ocultados do menu
* 🐞 Correção de bugs

### 1.23.0 - 24/11/2021 - Entregas da Sprint 32 (Urgências)
* UE > Foram feitas alterações de texto na Relação de Bens
* UE > Foram feitas alterações de texto no Demonstrativo Financeiro
* UE > O relatório de devolução para acertos em PDF agora inclui novo campo de detalhamento de ajustes em documento 
* UE > Foram feitas alterações de texto e cálculo nas atas de apresentação e retificação de PCs. 

### 1.22.0 - 18/11/2021 - Entregas da Sprint 31
* UE > Demonstrativos Financeiros agora são gerados apenas em PDF e não mais em Excel
* UE > Relações de Bens agora são gerados apenas em PDF e não mais em Excel
* UE > Agora é possível editar a implantação de valores reprogramados quando a PC inicial for devolvida para ajustes
* UE > Agora é possível informar quando o presidente da Associação está ausente e qual cargo o esta substituindo
* UE > Demonstrativos financeiros e Relações de Bens gerados durante a ausência do presidente terão o cargo substituto na linha de assinatura
* UE > Reformulada a ata de PC para incluir lista de presentes e distinguir melhor a ata do parecer do conselho fiscal
* UE > A consulta de resumo de acertos agora inclui o novo campo de detalhamento de acertos em documentos
* UE > Alterações menores em textos diversos
* 🐞 Correção de bugs

### 1.21.0 - 01/11/2021 - Entregas da Sprint 30
* UE > Melhorias diversas no layout do Demonstrativo Financeiro (PDF)
* UE > Novas notificações de devolução de PC até que usuário veja os ajustes solicitados
* DRE > Acompanhamento de PC agora exibe detalhes da última análise, quando nos status posteriores à análise
* DRE > Relatório de acertos solicitados agora é gerado automaticamente ao final da análise de prestação de contas
* DRE > Reprovação de PC agora permite a seleção de motivos pré-cadastrados
* DRE > Solicitação de acertos em documentos de PC agora inclui campo de detalhamento
* 🐞 Correção de bugs

### 1.20.0 - 18/10/2021 - Entregas da Sprint 29
* UE > Novo rodapé no relatório de Relação de Bens 
* UE > Filtro por vínculo de atividades em Gastos da Escola
* DRE > Relatório de acertos solicitados em análise de prestação de contas
* DRE > Novo processo de devolução de prestações de contas para acertos
* DRE > Inclusão de motivo de não regularidade de uma Associação
* ADM > Carga de repasses (previstos e realizados) agora permite reprocessamento sem duplicação
* 🐞 Correção de bugs

### 1.19.0 - 29/09/2021 - Entregas da Sprint 28
* UE > Consulta de detalhes de análises da DRE
* UE > Agora não é mais permitida a exclusão de créditos do tipo repasse
* UE > Melhoria na visualização de detalhes de uma Associação
* UE > Gastos da escola agora exibem as despesas com todos os seus rateios agrupados
* DRE > Conclusão do novo fluxo de acompanhamento de prestações de contas
* ADM > Registro de movimentações (Audit Logs) relacionadas à Associações
* ADM > Desativação de especificações de material ou serviço
* 🐞 Correção de bugs

### 1.18.0 - 08/09/2021 - Entregas da Sprint 27
* ADM > Registro de movimentações (Audit Logs) relacionadas à Prestação de Contas
* ADM > Registro de movimentações (Audit Logs) complementares de despesas e receitas
* ADM > Registro de movimentações (Audit Logs) relacionadas à visão DRE
* ADM > Registro de movimentações (Audit Logs) relacionadas à Usuários
* UE > Melhoria na comunicação com o usuário na exclusão de uma Associação
* DRE > Novo fluxo de acompanhamento de prestações de contas (partes 3 e 4)
* SME > Exportação de informações de extrato das Associações
* 🐞 Correção de bugs

### 1.17.0 - 26/08/2021 - Entregas da Sprint 26
* UE > Nova consulta Análises da DRE
* UE > Créditos da Escola agora não permite o lançamento de documentos em datas futuras
* UE > Gastos da Escola agora não permite o lançamento de documentos em datas futuras
* UE > Conciliação Bancária agora não permite o lançamento de saldos em datas futuras
* UE > Melhorias de usabilidade na exclusão de rateios de uma despesa
* UE > Créditos de recursos externos: indicativo visual de créditos sem gastos vinculados
* UE > Melhorias de usabilidade na inclusão de membros do tipo aluno
* UE > O presidente e secretário informados nas atas agora podem ser selecionados detre os membros da APM
* DRE > Novo fluxo de acompanhamento de prestações de contas (partes 1 e 2)
* DRE > Prévia de relatório consolidado agora é gerada assincronamente
* Nova Central de Downloads 
* 🐞 Correção de bugs

### 1.16.0 - 09/08/2021 - Entregas da Sprint 25
* UE > Agora é possível lançar despesas sem comprovação fiscal
* UE > Ficha cadastral atualizada automaticamente com informações do Eol
* UE > Novo bloco justificativas no demonstrativo financeiro em XLSX e PDF
* UE > Melhorias na usabilidade da Conciliação Bancária 
* DRE > Relatório consolidado agora é gerado assincronamente
* DRE > Melhorias na usabilidade do Acompanhamento de Prestação de Contas
* DRE > Melhorias na usabilidade do Relatório Consolidado
* DRE > Cadastro de Fornecedores
* SME > Parametrizações > Cadastro de Fornecedores
* Melhorias na Gestão de Perfis
* Ajustes em textos diversos
* 🐞 Correção de bugs

### 1.15.0 - 23/07/2021 - Entregas da Sprint 24
* UE > Exibição de totais de créditos no cadastramento de receitas
* UE > Exibição de mensagem parametrizavel ao usar determinados tipos de crédito
* UE > No cadastro de créditos, agora o campo detalhamento só é pedido para determinados tipos de crédito 
* UE > Implementado filtro por conta no cadastro de gastos da escola
* UE > Gastos da escola agora usa um formulário simplificado para editar gastos vinculados a recursos externos
* UE > Não é mais possível usar uma ação de recurso externo em uma despesa lançada em gastos da escola
* UE > Exibição de mensagem ao tetar excluir uma despesa usada em uma devolução ao tesouro
* DRE > Em acompanhamento de PC agora é possível consultar de uma vez PCs de todos os status
* DRE > Listas de unidades agora são ordenadas por status da PC, tipo de unidade e nome
* DRE > Ajustes em textos diversos
* DRE > Exibição de mensagem ao tentar reabrir ou devolver uma PC com PCs posteriores
* SME > Exibição da DRE da Associações no cadastro de Associações
* O usuário agora pode escolher exibir a senha digitada no formulário de login
* Notificações agora também são enviadas por e-mail para os usuários
* 🐞 Correção de bugs


### 1.14.0 - 08/07/2021 - Entregas da Sprint 23
* UE > Créditos de recursos externos agora permitem editar/excluir uma saída vinculada
* UE > Agora se um crédito de recurso externo é excluido a saída vinculada também é
* UE > Melhorias no formulário de lançamento de recursos externos
* UE > O cadastro de membros da Associação agora pede o CPF quando tratar-se de um aluno
* UE > O lançamento de despesas do tipo capital, agora não traz mas valor default para a quantidade de itens
* DRE > Resumo de Recursos, alterada a cor de destaques
* DRE > Ajustes em textos diversos
* 🐞 Correção de bugs


### 1.13.0 - 23/06/2021 - Entregas da Sprint 22
* UE > Notificações sobre a proximidade do inicio do período de prestação de contas
* UE > Notificações sobre inicio do período de prestação de contas
* UE > Notificações sobre a proximidade do fim do período de prestação de contas
* UE > Notificações sobre pendências de envio de prestações de contas
* UE > Notificações sobre ajustes solicitados pelas DREs em prestações de contas
* UE > Notificações sobre a proximidade do fim do prazo de entrega de ajustes solicitados em prestações de contas
* UE > Notificações sobre atrasos na entrega de ajustes solicitados em prestações de contas
* ADM > Cargas de repasse agora não criam mais tipos de conta e ações não existentes
* 🐞 Correção de bugs

### 1.12.0 - 08/06/2021 - Entregas da Sprint 21

* UE > Créditos não relativos ao PTRF agora permite Lançar saída do recurso na edição 
* UE > Melhorias na validação de campos no lançamento de despesas
* DRE > dados da diretoria não obriga mais a digitação do RF do diretor
* DRE > Controle de acesso de gravação em Dados da Diretoria
* DRE > Controle de acesso de gravação em Técnicos da DRE
* DRE > Controle de acesso de gravação em Atribuições de técnicos da DRE
* DRE > Controle de acesso de gravação em Processos SEI
* SME > Carga de  usuários a partir da gestão de perfis de acesso
* 🐞 Correção de bugs

### 1.11.0 - 21/05/2021 - Entregas da Sprint 20
* UE > Status "Incompleto" em despesas agora chama-se "Rascunho"
* UE > Despesas de status "Rascunho" agora são ignorados nos cálculos e relatórios
* UE > Tipo das unidades agora são atualizados automaticamente conforme EOL
* UE > Pagamentos em ordem cronológica no Demonstrativo Financeiro
* UE > Alterações menores em textos e usabilidade 
* UE > Melhorias de performance no lançamento de despesas
* DRE > Diretorias agora podem cadastrar usuários de suas subordinadas
* SME > Secretaria agora pode cadastrar usuários para qualquer unidade
* 🐞 Correção de bugs

### 1.10.0 - 06/05/2021 - Entregas da Sprint 19
* UE > Exportação de Atas em PDF
* ADM > Criação de usuários com atualização do CoreSSO
* ADM > Pesquisa por associação em Despesas 
* ADM > Carga de associações agora busca informações do EOL
* Alterações menores em textos
* Melhorias diversas de usabilidade
* 🐞 Correção de bugs

### 1.9.0 - 20/04/2021 - Entregas da Sprint 18
* ADM > Carga de usuários atualizando CoreSSO
* UE > Atualização de informações das escolas a partir do EOL agora inclui os CEUs
* UE > No lançamento de repasses agora é possível selecionar uma destinação específica
* UE > Demonstrativo Financeiro em PDF
* UE > Relação de Bens em PDF
* 🐞 Correção de alguns bugs

### 1.8.1 - 09/04/2021 - Hotfix
* Correção de erro de timeout na geração de prévias

### 1.8.0 - 06/04/2021 - Entregas da Sprint 17
* UE > Upload de extrato bancário na conciliação
* UE > Geração de prévias de documento de forma assíncrona
* UE > Lançamento de gastos não demonstrados anteriores ao período de implantação
* UE > Novo demonstrativo financeiro agora integrando todas as ações em uma conta 
* UE > Melhorias na interface de exportação de informações e ficha cadastral
* UE > Mudanças de textos nas atas de apresentação e retificação
* UE > Mudanças de textos no relatório Relação de Bens
* UE > Mais opções de permissões na funcionalidade de prestações de contas
* DRE > Mais opções de permissões na funcionalidade de gestão de regularidade
* SME > Consulta de saldos bancários por tipo de unidade, DRE e Unidade
* SME > Download de extratos bancários adicionados pelas UEs
* ADM > Melhoria no sistema de permissionamento
* ADM > Exibição do nome do ambiente (Produção, Homologação, etc.)
* 🐞 Correção de bugs

### 1.7.0 - 05/03/2021 - Entregas da Sprint 16
* UE > Ficha cadastral da associação e de seu presidente (PDF)
* UE > Várias melhorias no processo de conciliação bancária 
* ADM > Registro de movimentações nos arquivos de carga para fins de auditoria
* ADM > Carga de usuários agora atualiza o e-mail do usuário no CoreSSO
* ADM > Carga de usuários agora permite a atualização dos grupos de acesso do usuário
* 🐞 Correção de bugs


### 1.6.0 - 16/02/2021 - Entregas da Sprint 15
* Informações do usuário agora no topo da tela
* UE > Campos para telefone e endereço no cadastro do presidente da associação
* SME > Cadastro de Tipos de Custeio
* SME > Cadastro de Etiquetas (Tags)
* SME > Edição dos textos "Fique de olho"
* SME > Carga de associações
* Ajustes em textos diversos
* 🐞 Correção de bugs

### 1.5.0 - 02/02/2021 - Entregas da Sprint 14
* DRE > Melhorias no relatório consolidado
* DRE > Motivos de aprovação com ressalvas no acompanhamento de PCs
* DRE > Seleção de período do acompanhamento de PCs agora inicia com o período anterior e não o corrente
* DRE > Novo bloco "Associações não regularizadas" no relatório consolidado DRE
* SME > Cadastro de Associações
* SME > Cadastro de Ações
* SME > Cadastro de vínculos de ações e associações
* SME > Cadastro de Períodos
* UE > Melhorias na geração de prestações de contas
* UE > Cadastro de membros agora vincula automaticamente o membro ao seu usuário do sistema 
* ADM > Agora é possivel fazer carga de associações sem CNPJ
* ADM > Pesquisa por nome nas tabelas de ações da associação e contas da associação

### 1.4.0 - 07/01/2021 - Entregas da Sprint 13
* Visão SME
* DRE > Painel de parâmetros do sistema
* SME > Acompanhamento de prestações de conta > Resumo Geral
* SME > Acompanhamento de prestações de conta > Resumo por DRE (lista)
* Lançamento de Créditos não relativos ao PTRF
* Melhorias na área de administração do sistema
* Melhorias na Ata de Retificação
* Seleção de repasses ao cadastrar créditos
* Recurso de exclusão de membros da associação
* Melhorias no acompanhamento de prestações de contas da DRE
* 🐞 Correção de alguns poucos bugs ;-)

### 1.3.0 - 08/12/2020 - Entregas da Sprint 12
* Carga de previsões de repasse da SME;
* Carga de quantidade de alunos do último celso;
* Vínculo de membros da associação a seus usuários no sistema;
* Uso do CPF para identificar membros de associação que são pais ou responsáveis;
* Configurado monitoramento de erros (Sentry);
* Dashboard da DRE movido para o ítem de menu 'Acompanhamento';
* Melhoria no texto da mensagem de alerta sobre períodos bloqueados para alteração;
* Melhorias na navegação entre informações na consulta de Associações pela DRE;
* Uso de perfis de acesso nas ações da consulta de Associações pela DRE;
* Aplicação de máscara na digitação do processo SEI de regularidade da Associação;
* Mensagem de confirmação de gravação ao atualizar dados da DRE;
* Geração de documentos de prestação de contas de forma assíncrona;
* Relatório Consolidado DRE (Parte 2);
* Mudança no critério de 'Prestações de Contas Não Recebidas' no painel da DRE;
* No painel da DRE, o total de associações passa a desconsiderar associações sem CNPJ;
* Geração de notificações para o presidente e vice-presidente da associação, sobre comentários feitos pela DRE na análise de uma prestação de contas;  
* Bloqueio de conciliação de lançamentos em períodos fechados;
* Restrições de edição para a associação em devoluções ao tesouro registradas pela DRE;
* Na inclusão/edição de despesas, mensagem de confirmação ao sair, apenas quando houver mudanças;
* Expiração de acesso do usuário após 10 horas de logado;  
* Ajustes menores em textos e labels;
* 🐞 Correção de alguns bugs.


### 1.2.0 - 10/11/2020 - Entregas da Sprint 11
* Gestão de perfis de acesso às funcionalidades do sistema
* Cadastro de Devoluções ao Tesouro na análise de prestações de conta pela DRE
* Inclusão de comentários na análise de prestações de conta pela DRE
* Atas de retificação
* Relatório Consolidado DRE (Parte 1)
* Permitir a parametrização de um tipo de conta para apenas leitura
* Saldos negativos agora são exibidos em vermelho no painel financeiro da Associação
* Melhorias diversas no processo de cargas de dados da aplicação
* Recuperação de senha ("esqueci minha senha") agora usa o e-mail cadastrado no CoreSSO
* Inclusão de campos para telefone e e-mail no cadastro de técnicos da DRE
* Mudanças nos filtros do cadastro de créditos da Associação
* Mudança na forma de exibição da visão do usuário, agora ao lado do seletor de unidade
* 🐞 Correção de alguns bugs.

### 1.1.0 - 09/10/2020 - Entregas da Sprint 10
* Parametrização de tipos de crédito por conta
* Ata consolidada por prestação de contas (todos as contas)
* Excluida opção de aprovação com ressalva de uma ata
* Uso de campos default na criação de uma conta
* Mensagem de tempo de transação não demonstrada na conciliação agora é em meses
* Validação de cadastros repetidos de membros da Associação
* O cadastro de crédito agora só confirma a saida da edição se tiver ocorrido alguma alteração
* Relação de bens agora só é gerada quando há aquisição de bens no período
* Dashboard da DRE para acompanhamento de prestações de contas
* Lista de prestações de contas por status
* Workflow de acompanhamento de prestações de contas pela DRE
* 🐞 Correção de alguns bugs.

### 1.0.0 - 15/09/2020 - Entregas da Sprint 9
* Entrada em produção (Piloto com algumas Associações)
* Desacoplamento dos processos de conciliação e prestação de contas;
* Transações já conciliadas, quando modificadas, voltam ao estado de não conciliadas;
* Alteração do processo de prestação de contas para incluir todas as contas da Associação em vez de ser uma prestação por conta;
* Prévias parciais para os relatórios de demonstrativo financeiro e relação de bens da prestação de contas;
* Melhorias no painel financeiro das associações;
* Na visão DRE, consulta da situação financeira de uma associação;
* Central de Notificações;
* Apoio à Diretoria: FAQ;
* Demonstrativos financeiros e relações de bens agora incluem a data de geração do documento;
* Na visão DRE, consulta de dados das Unidades Educacionais trazendo informações do EOL;
* Atribuições de Técnicos da DRE à Unidades Educacionais;
* Possibilidade de copiar atribuições de técnicos de um outro período;
* Transferência de atribuições de um técnico para outro no momento de uma exclusão de técnico;
* Aprimoramentos no relatório de demonstrativo financeiro;
* 🐞 Correção de alguns erros.


### 0.7.0 - 20/08/2020 - Entregas da Sprint 8
* Exportação de dados da Associação;
* Gestão de valor realizado nas despesas da Associação;
* Notificação de transações não demonstradas a mais de certo tempo;
* Prestação de contas: Permitir selecionar apenas períodos até o próximo período pendente;
* Atualiza carga de usuários para incluir a visão (UE, DRE ou SME);
* Menus sensíveis às visões UE e DRE;
* Permite ao usuário alternar entre visões e unidades (UEs ou DREs);
* Lista de associações da DRE;
* Consulta dados de uma associação da DRE;
* Consulta dados de uma UE da DRE;
* Cadastro de processos SEI de regularidade e prestação de contas de uma Associação;
* Checklists de regularidade de uma associação da DRE;
* Consulta de dados da DRE;
* Cadastro de técnicos da DRE.

### 0.6.0 - 28/07/2020 - Entregas da Sprint 7
* Carga de valores reprogramados (implantação de saldos);
* Novos campos (e-mail e CCM) no cadastro da Associação;
* Processo de recuperação de senha ("Esqueci minha senha");
* Perfil do usuário com possibilidade de troca de e-mail e senha;
* Permitir parametrizar tipos de documento de despesas para pedirem ou não o número do documento;
* Edição via Admin do texto exibido no "Fique de Olho" em prestações de contas;
* Em prestações de contas exibir demonstrativos financeiros apenas par ações com saldo ou movimentação;
* Na Ata exibir apenas ações que tenham saldos ou movimentação no período;
* Em despesas trazer o automaticamente o valor do rateio quando não houver multiplos rateios;
* No painel de ações exibir apenas ações que tenham saldo ou movimentação no período;
* Ajustes na formatação de valores do demonstrativo financeiro;
* Desconsiderar acentuações no filtro de despesas;
* Desconsiderar acentuações no filtro de receitas;
* Pedir período de referência em créditos do tipo devolução;
* Apresentar na Ata os créditos de devolução;
* Permitir criar tags e associa-las a uma despesa.  
* 🐞 Correção de erros diversos.

### 0.5.0 - 07/07/2020 - Entregas da Sprint 6
* Confirmação de repasses na entrada de créditos agora considera a classificação da receita em capital ou custeio;
* Alterada a estrutura do Demonstrativo Financeiro;
* Lançamento de saldos reprogramados (implantação de saldos);
* Cadastramento de todos os cargos da Associação;
* Cadastramento de dados das contas da Associação;
* Verificação de duplicidade no lançamento de uma despesa;
* CNPJ/CPF do fornecedor agora é brigatório no lançamento de uma despesa;
* Períodos futuros não são mais exibidos no painel de ações;
* Implementadas buscas por data e fornecedor na consulta de despesas;
* Implementada busca por data na consulta de créditos;
* Parametrização por tipo de documento para aceitar apenas dígitos no lançamento de despesas;
* Criado campo para detalhamento de créditos parametrizavel por tipo de crédito;
* O campo de observação da prestação de contas agora é vinculado à ação da associação;
* Exibição de valores de créditos futuros na ata da prestação de contas;
* Exibição do nome da escola abaixo do usuário em vez do nome da associação; 
  
### 0.4.0 - 16/06/2020 - Entregas da Sprint 5
* Geração do documento Relação de Bens na prestação de contas
* Adicionado campo "Nº do cheque" no lançamento de despesas
* Geração da Ata na prestação de contas
* Adicionada a verificação de suficiência de saldo por conta no lançamento de despesas
* Exibição de tabela de valores pendentes no processo de conciliação
* Melhoria na mensagem de validação de consistência de valores no lançamento de despesas
* Adicionada rotina de carga de dados para valores realizados por associação
* Seleção de período na prestação de contas não exibe mais períodos futuros
* Lista de especificações de materiais serviços agora é exibida em ordem alfabética
* Agora é possível determinar a ordem que as ações serão exibidas no painel de ações e em outras partes da aplicação
* Adicionado feedback visual (loading) para processos demorados no módulo de receitas
* Agora a conciliação exibe transações não conciliadas mesmo de períodos anteriores
* 🐞 Correção de erros

### 0.3.0 - 28/05/2020 - Entregas da Sprint 4
* Exibição de referência e status do período no painel de ações
* Alteração automática do status do período na associação
* Exibição de outras receitas no painel de ações
* Navegação entre períodos no painel de ações
* Alerta no lançamento de despesas acima do saldo por ação
* Exibição de totais de despesas em Gastos da Escola
* Categorização de receitas em Custeio e Capital
* Destacar campos incompletos no cadastro de despesa
* Inicio do processo de prestação de contas
* Conciliação de lançamentos na prestação de contas
* Bloqueio de alterações em receitas de períodos fechados
* Bloqueio de alterações em despesas de períodos fechados
* Geração de demonstrativo financeiro

### 0.2.0 - 28/04/2020 - Entregas da Sprint 3
* Carga de Associações
* Carga de Usuários
* Carga de Repasses
* Cadastro de Períodos de realização de despesas
* Registro de alterações (Audit Logs) de Despesas
* Registro de alterações (Audit Logs) de Receitas
* Consulta de despesas no Admin
* Consulta de receitas no Admin
* Confirmação de repasses pela Associação
* Alerta na despesa sobre o uso de especificações do Sistema de Bens Patrimoniais Móveis do PMSP
* Filtros diversos para consulta de despesas
* Filtros diversos para consulta de receitas
* Cadastro de Associações
* Registro de fornecedores usados
* Consulta de informações para o Painel de Ações da Associação

### 0.1.0 - 07/04/2020 - Entregas da Sprint 2
* Autenticação de usuário
* Cadastro de despesas
* Cadastro de receitas
* Carga da tabela de especificações

### Para desenvolver

I)  Clone o repositório.
```console
$ git clone https://github.com/prefeiturasp/SME-PTRF-BackEnd.git back
$ cd back
```

II)  Crie um Virtualenv com Python 3.6
```console
$ python -m venv .venv
```

III.  Ative o Virtualenv.
```console
$ source .venv/bin/activate
```

IV.  Instale as dependências.
```console
$ pip install -r requirements\local.txt
```

V.  Configure a instância com o .env
```console
$ cp env_sample .env
```

VI.  Execute os testes.
```console
$ pytest
```

VII.  Faça um Pull Request com o seu desenvolvimento

## Executando com docker 

I. Clone o repositório
```console
$ git clone git@github.com:prefeiturasp/SME-PTRF-BackEnd.git back
```

II. Entre no diretório criado
```console
$ cd back
```

III. cp env_sample .env
```console
$ cp env-sample
```

IV. Execute o docker
```console
$ docker-compose -f local.yml up --build -d
```

V. Crie um super usuário no container criado
```console
$ docker-compose -f local.yml run --rm django sh -c "python manage.py createsuperuser"
```

VI. Acesse a url para verificar a versão (Faça o login primeiro com o usuário criado).
```console
http://localhost:8000/api/versao
```

### Filas Celery
**Subir o Celery Worker**
```console
$ celery  -A config worker --loglevel=info
```

**Subir o Celery Beat**
```console
$ celery  -A config beat --loglevel=info
```

**Monitorar os processos no celery**
```console
$ flower -A config --port=5555
```

**Limpar os processos no celery**
```console
$ celery  -A config purge
```
