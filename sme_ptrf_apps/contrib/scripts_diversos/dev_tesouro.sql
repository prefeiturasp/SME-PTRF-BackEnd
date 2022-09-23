-- noinspection SqlNoDataSourceInspectionForFile

-- Lista solicitações de devolução ao tesouro sem uma devolução ao tesouro vinculada
select
a.unidade_id as "codigo_eol",
a.nome,
pc.id as "pc_id",
p.referencia,
d.id as "despesa_id", d.numero_documento,
count(sal.id)
from
core_prestacaoconta as pc,
core_periodo as p,
core_associacao as a,
core_analiseprestacaoconta as apc,
core_analiselancamentoprestacaoconta as al,
despesas_despesa as d,
core_solicitacaoacertolancamento as sal,
core_tipoacertolancamento as tal
where
pc.periodo_id = p.id
and pc.associacao_id = a.id
and apc.prestacao_conta_id = pc.id
and al.analise_prestacao_conta_id = apc.id
and al.despesa_id = d.id
and sal.analise_lancamento_id = al.id
and tal.id = sal.tipo_acerto_id
and tal.categoria = 'DEVOLUCAO'
and sal.devolucao_ao_tesouro_id is null
group by
pc.id,
p.referencia,
a.unidade_id,
a.nome,
d.id, d.numero_documento, d.valor_total
order by
a.unidade_id,
a.nome,
p.referencia,
d.id, d.numero_documento, d.valor_total


-- Lista de Prestações de Conta com devoluções ao tesouro faltando
select
a.unidade_id as "codigo_eol",
a.nome,
pc.id as "pc_id",
p.referencia
from
core_prestacaoconta as pc,
core_periodo as p,
core_associacao as a,
core_analiseprestacaoconta as apc,
core_analiselancamentoprestacaoconta as al,
despesas_despesa as d,
core_solicitacaoacertolancamento as sal,
core_tipoacertolancamento as tal
where
pc.periodo_id = p.id
and pc.associacao_id = a.id
and apc.prestacao_conta_id = pc.id
and al.analise_prestacao_conta_id = apc.id
and al.despesa_id = d.id
and sal.analise_lancamento_id = al.id
and tal.id = sal.tipo_acerto_id
and tal.categoria = 'DEVOLUCAO'
and sal.devolucao_ao_tesouro_id is null
group by
pc.id,
p.referencia,
a.unidade_id,
a.nome
order by
a.unidade_id,
a.nome,
p.referencia
