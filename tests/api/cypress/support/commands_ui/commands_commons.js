import Commons_Locators from '../locators/commons_locators'

const commons_locators = new Commons_Locators

Cypress.Commands.add('validar_mensagens_comuns_do_sistema', (mensagem) => {
    const mensagensErro = [
        'Nome é obrigatório',
        'CPF / CNPJ é obrigatório',
        'Digite um CPF / CNPJ válido',
		'Nome do motivo é obrigatório',
		'Este motivo de pagamento antecipado já existe.',
    ];

	const mensagensErroNovoPadraoExclusao = [
        'Tem certeza que deseja excluir esse tipo de documento?',
    ];

	const mensagensValidacao = [
		'Este tipo de documento já existe.',
		'Já existe um tipo de transação com esse nome',
		'Deseja realmente excluir este tipo de transação?'
	]
	
    const mensagensSucesso = [
        'O fornecedor foi adicionado ao sistema com sucesso.',
        'O tipo de documento foi editado no sistema com sucesso.',
		'Não foi possível criar o fornecedor',
		'O fornecedor foi editado no sistema com sucesso.',
		'O fornecedor foi removido do sistema com sucesso.',
		'O motivo de pagamento antecipado foi adicionado ao sistema com sucesso.',
		'O motivo de pagamento antecipado foi editado no sistema com sucesso.',
		'O tipo de conta foi removido do sistema com sucesso.',
		'O motivo de pagamento antecipado foi removido do sistema com sucesso.',
		'O tipo de conta foi adicionado ao sistema com sucesso.',
		'O tipo de conta foi editado no sistema com sucesso.',
		'O tipo de conta foi removido do sistema com sucesso.',
		'O tipo de documento foi adicionado ao sistema com sucesso.',
		'Já existe um tipo de conta com esse nome.',
		'O tipo de documento foi removido do sistema com sucesso.',
		'O tipo de transação foi adicionado ao sistema com sucesso.',
		'O tipo de transação foi removido do sistema com sucesso.',
		'O tipo de transação foi editado no sistema com sucesso.'
    ];

    if (mensagensErro.includes(mensagem)) {
        cy.get(commons_locators.msg_erro_modal()).should('be.visible').and('contain', mensagem);
    } else if (mensagensSucesso.includes(mensagem)) {
        cy.get(commons_locators.msg_cadastro()).should('be.visible').and('contain', mensagem);
    }  else if (mensagensErroNovoPadraoExclusao.includes(mensagem)) {
        cy.get(commons_locators.mensagensErroNovoPadraoExclusao()).should('be.visible').and('contain', mensagem);
    } else if (mensagensValidacao.includes(mensagem)) {
		cy.get(commons_locators.msg_modal_confirmacao_exclusao()).should('be.visible').and('contain', mensagem);
	}else {
        throw new Error(`Mensagem inesperada: ${mensagem}`);
    }
});


Cypress.Commands.add('validar_mensagem_de_exclusao', (mensagem_de_confirmacao_de_erro) => {
	cy.get(commons_locators.msg_modal_confirmacao_exclusao()).should('be.visible').and('contain', mensagem_de_confirmacao_de_erro);
})

Cypress.Commands.add('configurar_visualizacao', (device) => {
	cy.visit(Cypress.config('baseUrlPTRFHomol'))
	switch (device) {
		case 'web':
			cy.viewport(1920, 1080)
			break
		default:
			break
	}
})

Cypress.Commands.add('validar_resultado_da_consulta', (resutado_consulta) => {
	cy.get(commons_locators.tbl_resultados_motivo_de_pagamento_antecipado()).should('be.visible').and('contain', resutado_consulta);
})