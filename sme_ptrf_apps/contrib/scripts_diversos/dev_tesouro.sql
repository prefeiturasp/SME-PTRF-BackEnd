-- noinspection SqlNoDataSourceInspectionForFile

-- Lista solicitações de devolução ao tesouro sem uma devolução ao tesouro vinculada
select
a.unidade_id as "codigo_eol",
u.nome,
pc.id as "pc_id",
p.referencia,
d.id as "despesa_id", d.numero_documento, d.valor_total
from
core_prestacaoconta as pc,
core_periodo as p,
core_associacao as a,
core_unidade as u,
core_analiseprestacaoconta as apc,
core_analiselancamentoprestacaoconta as al,
despesas_despesa as d,
core_solicitacaoacertolancamento as sal,
core_tipoacertolancamento as tal
where
pc.periodo_id = p.id
and a.unidade_id = u.codigo_eol
and pc.associacao_id = a.id
and apc.prestacao_conta_id = pc.id
and al.analise_prestacao_conta_id = apc.id
and al.despesa_id = d.id
and sal.analise_lancamento_id = al.id
and tal.id = sal.tipo_acerto_id
and tal.categoria = 'DEVOLUCAO'
and (select count(dt.id) from core_devolucaoaotesouro as dt where dt.prestacao_conta_id = pc.id and dt.despesa_id = d.id) = 0
group by
pc.id,
p.referencia,
a.unidade_id,
u.nome,
d.id, d.numero_documento, d.valor_total
order by
a.unidade_id,
u.nome,
p.referencia,
d.id, d.numero_documento

-- Lista de Prestações de Conta com devoluções ao tesouro faltando
select
a.unidade_id as "codigo_eol",
u.nome,
pc.id as "pc_id",
p.referencia
from
core_prestacaoconta as pc,
core_periodo as p,
core_associacao as a,
core_unidade as u,
core_analiseprestacaoconta as apc,
core_analiselancamentoprestacaoconta as al,
despesas_despesa as d,
core_solicitacaoacertolancamento as sal,
core_tipoacertolancamento as tal
where
pc.periodo_id = p.id
and a.unidade_id = u.codigo_eol
and pc.associacao_id = a.id
and apc.prestacao_conta_id = pc.id
and al.analise_prestacao_conta_id = apc.id
and al.despesa_id = d.id
and sal.analise_lancamento_id = al.id
and tal.id = sal.tipo_acerto_id
and tal.categoria = 'DEVOLUCAO'
and (select count(dt.id) from core_devolucaoaotesouro as dt where dt.prestacao_conta_id = pc.id and dt.despesa_id = d.id) = 0
group by
pc.id,
p.referencia,
a.unidade_id,
u.nome
order by
a.unidade_id,
u.nome,
p.referencia

-- Lista solicitações de devolução ao tesouro sem uma devolução ao tesouro vinculada com info de solicitação de devolução
select
a.unidade_id as "codigo_eol",
u.nome,
pc.id as "pc_id",
p.referencia,
d.id as "despesa_id", d.numero_documento, d.valor_total,
sdt.id as solicitacao_dev
from
core_prestacaoconta as pc,
core_periodo as p,
core_associacao as a,
core_unidade as u,
core_analiseprestacaoconta as apc,
core_analiselancamentoprestacaoconta as al,
despesas_despesa as d,
core_solicitacaoacertolancamento as sal,
core_tipoacertolancamento as tal,
core_solicitacaodevolucaoaotesouro as sdt
where
pc.periodo_id = p.id
and a.unidade_id = u.codigo_eol
and pc.associacao_id = a.id
and apc.prestacao_conta_id = pc.id
and al.analise_prestacao_conta_id = apc.id
and al.despesa_id = d.id
and sal.analise_lancamento_id = al.id
and tal.id = sal.tipo_acerto_id
and sdt.solicitacao_acerto_lancamento_id = sal.id
and tal.categoria = 'DEVOLUCAO'
and (select count(dt.id) from core_devolucaoaotesouro as dt where dt.prestacao_conta_id = pc.id and dt.despesa_id = d.id) = 0
group by
pc.id,
p.referencia,
a.unidade_id,
u.nome,
d.id, d.numero_documento, d.valor_total,
sdt.id
order by
a.unidade_id,
u.nome,
p.referencia,
d.id, d.numero_documento
