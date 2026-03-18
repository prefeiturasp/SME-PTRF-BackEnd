class Resumo_dos_recursos_Localizadores {
	// tela resumo dos recursos consulta
	aba_resumo_dos_recursos = () => { return '[data-cy="Resumo dos recursos"]' }
	flt_periodo_resumo_dos_recursos = () => { return ':nth-child(2) > #periodo' }
	flt_conta_resumo_dos_recursos = () => { return ':nth-child(4) > #periodo' }
	cards_resumo_dos_recursos = () => { return '.card > .card-header' }
	cards_saldos_resumo_dos_recursos = () => { return 'div > p.pt-0' }
	cards_saldo_reprogramado_resumo_dos_recursos = () => { return '.pt-1.mb-4' }
	cards_todos_saldos_reprogramados_resumo_dos_recursos = () => { return '.pt-1.mb-4 strong' }
	tbl_periodo_resumo_dos_recursos = () => { return ':nth-child(1) > .card > .card-header' }	
	
}

export default Resumo_dos_recursos_Localizadores