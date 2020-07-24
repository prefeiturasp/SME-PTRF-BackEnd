# SME-PTRF-BackEnd
========

API da aplicação *SIG.Escola* da Secretaria de Educação da cidade de São Paulo.

License: MIT

Versão: 0.6.0


## Release Notes

### 0.6.0 - 28/07/2020 - Entregas da Sprint 7

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
