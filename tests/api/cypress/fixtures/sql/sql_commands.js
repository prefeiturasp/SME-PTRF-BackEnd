export function delete_tipo_de_conta(nome) {
	return `delete from core_tipoconta where nome = '${nome}'`
}

export function insert_tipo_de_conta(nome) {
	return `INSERT INTO core_tipoconta(
	nome, criado_em, alterado_em, uuid, agencia, banco_nome, numero_cartao, numero_conta, apenas_leitura, permite_inativacao)
	VALUES ('${nome}', now(), now(), 'd2db175f-9e8a-4f21-9778-c26ec84bf1de', '0001', 'teste automatizado', '1234432112344321', '12345', true, true);`
}

export function delete_fornecedores(nome) {
	return `delete from despesas_fornecedor where nome = '${nome}'`
}

export function insert_fornecedor(nome, cpf_cnpj) {
	return `INSERT INTO public.despesas_fornecedor(
	criado_em, alterado_em, uuid, cpf_cnpj, nome)
	VALUES (now(), now(), '89926038-6bfd-4697-b9aa-76c9a9b2760f', ${cpf_cnpj}, '${nome}');`
}

export function delete_motivo_pagamento_antecipado(motivo) {
	return `delete from despesas_motivopagamentoantecipado where motivo = '${motivo}'`
}

export function insert_motivo_pagamento_antecipado(motivo) {
	return `INSERT INTO public.despesas_motivopagamentoantecipado(
	criado_em, alterado_em, uuid, motivo)
	VALUES (now(), now(), '89926038-6bfd-4697-b9aa-76c9a9b2760f' ,'${motivo}');`
}

export function delete_tipo_do_documento(nome) {
	return `delete from despesas_tipodocumento where nome = '${nome}'`
}

export function insert_tipo_do_documento(nome) {
	return `INSERT INTO public.despesas_tipodocumento(
	nome, criado_em, alterado_em, uuid, apenas_digitos, numero_documento_digitado, eh_documento_de_retencao_de_imposto, pode_reter_imposto, documento_comprobatorio_de_despesa)
	VALUES ('${nome}', now(), now(), '206bbabd-234f-4438-8cf2-218f875a6dd5', 'true', 'true', 'true', 'true', 'true');`
}

export function delete_tipo_de_transacao(nome) {
	return `delete from despesas_tipotransacao where nome = '${nome}'`
}

export function insert_tipo_de_transacao(nome) {
	return `INSERT INTO public.despesas_tipotransacao(
	nome, criado_em, alterado_em, uuid, tem_documento)
	VALUES ('${nome}', now(), now(), '206bbabd-234f-4438-8cf2-218f875a6dd5', true);`
}


