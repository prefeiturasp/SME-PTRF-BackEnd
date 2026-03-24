import Creditos_da_Escola_Localizadores from '../locators/creditos_da_escola_locators'

const creditos = new Creditos_da_Escola_Localizadores()

Cypress.Commands.add('clicar_creditos_da_escola', () => { 
  cy.get(creditos.menu_creditos_da_escola(), { timeout: 10000 })
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_creditos_da_escola', (campo) => {

  const mapaCampos = {
    sem_filtros_aplicados: creditos.tbl_sem_filtros_aplicados,
    filtros_aplicados: creditos.tbl_filtros_aplicados,
    tipo: creditos.tbl_tipo,
    conta: creditos.tbl_conta,
    acao: creditos.tbl_acao,
    data: creditos.tbl_data,
    valor: creditos.tbl_valor,
  }

  const seletor = mapaCampos[campo]

  if (!seletor) {
    throw new Error(`Campo "${campo}" não mapeado`)
  }

  cy.get(seletor())
    .should('be.visible')
    .and(($el) => {
      const texto = $el.text().trim()
      expect(texto, `${campo}`).to.not.eq('')
    })
})

Cypress.Commands.add('validar_somas_creditos_ue', () => {

  const normalizar = (texto) => texto.replace(/\s+/g, ' ').trim()

  const formatarMoeda = (valor) => {
    return valor.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    })
  }

  cy.gerar_token().then((token) => {

    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/receitas/totais/',
      qs: {
        associacao_uuid: 'e4184fb0-3e9a-4539-9d0b-5a47f61996fe',
        tipo_receita: '',
        acao_associacao__uuid: '',
        conta_associacao__uuid: ''
      },
      headers: {
        Authorization: `JWT ${token}`,
        'x-recurso-selecionado': '3aa98008-b255-492c-9665-ed5e153cb82a'
      }
    }).then((response) => {

      expect(response.status).to.eq(200)

      const totalSemFiltro = response.body.total_receitas_sem_filtro
      const totalComFiltro = response.body.total_receitas_com_filtro

      const valorSemFiltroFormatado = formatarMoeda(totalSemFiltro)
      const valorComFiltroFormatado = formatarMoeda(totalComFiltro)

      cy.get(creditos.tbl_sem_filtros_aplicados())
        .should('be.visible')
        .invoke('text')
        .then((textoUI) => {
          expect(normalizar(textoUI))
            .to.equal(normalizar(valorSemFiltroFormatado))
        })

      cy.get(creditos.tbl_filtros_aplicados())
        .should('be.visible')
        .invoke('text')
        .then((textoUI) => {
          expect(normalizar(textoUI))
            .to.equal(normalizar(valorComFiltroFormatado))
        })
    })
  })
})

Cypress.Commands.add('selecionar_filtro_creditos_da_escola', (campo) => {
  const mapaTexto = {
    devolucao: 'Devolução à conta',
    estorno: 'Estorno',
    externo: 'Recurso Externo',
    rendimento: 'Rendimento',
    repasse: 'Repasse',
    todas: 'todas'
  }

  const textoEsperado = mapaTexto[campo]

  if (!textoEsperado) {
    throw new Error(`Filtro "${campo}" não mapeado`)
  }

  const normalizar = (texto) =>
    texto.replace(/\s+/g, ' ').trim().toLowerCase()

  cy.get(creditos.filtrar_por(), { timeout: 10000 })
    .should('be.visible')

  cy.get(`${creditos.filtrar_por()} option`, { timeout: 15000 })
    .should(($options) => {
      expect($options.length, 'options carregadas').to.be.greaterThan(1)
    })
    .then(($options) => {
      const option = [...$options].find((opt) =>
        normalizar(opt.text) === normalizar(textoEsperado)
      )

      if (!option) {
        const lista = [...$options].map((o) => `"${o.text.trim()}"`).join(', ')
        throw new Error(`Opção "${textoEsperado}" não encontrada. Disponíveis: ${lista}`)
      }

      cy.get(creditos.filtrar_por()).select(option.value)
    })

  cy.get(creditos.btn_filtrar())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_filtro_selecionado_creditos_da_escola', (campo) => {
  const mapaTexto = {
    devolucao: 'Devolução à conta',
    estorno: 'Estorno',
    externo: 'Recurso Externo',
    rendimento: 'Rendimento',
    repasse: 'Repasse',
    todas: 'todas'
  }

  const textoEsperado = mapaTexto[campo]

  const normalizar = (texto) =>
    texto.replace(/\s+/g, ' ').trim().toLowerCase()

  cy.get(`${creditos.filtrar_por()} option:selected`, { timeout: 10000 })
    .invoke('text')
    .then((textoSelecionado) => {
      expect(normalizar(textoSelecionado)).to.equal(normalizar(textoEsperado))
    })
})

Cypress.Commands.add('validar_total_filtrado_repasse_creditos_ue', () => {
  const associacaoUuid = 'e4184fb0-3e9a-4539-9d0b-5a47f61996fe'
  const recursoSelecionado = '3aa98008-b255-492c-9665-ed5e153cb82a'
  const tipoReceitaRepasse = '1'

  const normalizarTexto = (texto) => texto.replace(/\s+/g, ' ').trim()

  const formatarMoedaBR = (valor) => {
    return Number(valor || 0).toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    })
  }

  const extrairValorNumerico = (item) => {
    const candidatos = [
      item.valor,
      item.valor_receita,
      item.valor_total,
      item.valor_original,
      item.valor_credito,
      item.total,
      item.montante
    ]

    const encontrado = candidatos.find((v) => v !== undefined && v !== null)

    return Number(encontrado || 0)
  }

  cy.get(creditos.filtrar_por(), { timeout: 10000 })
    .should('be.visible')
    .select('Repasse')

  cy.get(creditos.btn_filtrar())
    .should('be.visible')
    .click()

  cy.gerar_token().then((token) => {
    cy.request({
      method: 'GET',
      url: `${Cypress.config('baseUrlPTRFHomol')}api/receitas/`,
      qs: {
        search: '',
        associacao__uuid: associacaoUuid,
        tipo_receita: tipoReceitaRepasse,
        acao_associacao__uuid: '',
        conta_associacao__uuid: ''
      },
      headers: {
        Authorization: `JWT ${token}`,
        'x-recurso-selecionado': recursoSelecionado,
        Accept: 'application/json'
      }
    }).then((response) => {
      expect(response.status).to.eq(200)

      const body = response.body
      const lista = Array.isArray(body)
        ? body
        : Array.isArray(body.results)
          ? body.results
          : []

      const somaApi = lista.reduce((acc, item) => {
        return acc + extrairValorNumerico(item)
      }, 0)

      const valorFormatadoApi = formatarMoedaBR(somaApi)

      cy.get(creditos.tbl_filtros_aplicados(), { timeout: 10000 })
        .should('be.visible')
        .invoke('text')
        .then((textoUI) => {
          expect(normalizarTexto(textoUI)).to.equal(normalizarTexto(valorFormatadoApi))
        })
    })
  })
})

Cypress.Commands.add('acionar_mais_filtros_creditos_da_escola', () => {
  cy.get(creditos.mais_filtros(), { timeout: 3000 })
    .should('be.visible')
    .click()
})

Cypress.Commands.add('preencher_filtro_detalhamento_credito', (detalhamento) => {
  cy.get(creditos.detalhamento_credito(), { timeout: 3000 })
    .should('be.visible')
    .clear()
    .type(detalhamento)
})

Cypress.Commands.add('preencher_filtro_conta_creditos_da_escola', () => {
  cy.get(creditos.filtrar_conta(), { timeout: 3000 })
    .should('be.visible')
    .select('Cheque')
})

Cypress.Commands.add('preencher_filtro_acao_creditos_da_escola', (acao) => {
  cy.get(creditos.acao(), { timeout: 3000 })
    .should('be.visible')
    .select(acao)
})

Cypress.Commands.add('preencher_filtro_periodo_de_creditos_da_escola', (dataDe) => {
  cy.get(creditos.filtrar_periodo_de(), { timeout: 3000 })
    .should('be.visible')
    .clear()
    .type(dataDe)
    .blur()
})

Cypress.Commands.add('preencher_filtro_periodo_ate_creditos_da_escola', (dataAte) => {
  cy.get(creditos.filtrar_periodo_ate(), { timeout: 3000 })
    .should('be.visible')
    .clear()
    .type(dataAte + '{enter}')
})

Cypress.Commands.add('preencher_filtros_creditos_da_escola_por_caso', (caso) => {
  switch (caso.toLowerCase()) {
    case 'detalhamento do crédito':
      cy.preencher_filtro_detalhamento_credito('Fevereiro')
      break

    case 'conta':
      cy.preencher_filtro_conta_creditos_da_escola('Cheque')
      break

    case 'ação':
    case 'acao':
      cy.preencher_filtro_acao_creditos_da_escola('PTRF Básico')
      break

    case 'período de':
    case 'periodo de':
      cy.preencher_filtro_periodo_de_creditos_da_escola('01/01/2026')
      break

    case 'período até':
    case 'periodo até':
    case 'periodo ate':
      cy.preencher_filtro_periodo_ate_creditos_da_escola('31/12/2026')
      break

    default:
      throw new Error(`Caso de filtro não mapeado: ${caso}`)
  }
})

Cypress.Commands.add('validar_filtro_detalhamento_credito', (detalhamento) => {
  cy.get(creditos.detalhamento_credito(), { timeout: 10000 })
    .should('be.visible')
    .should('have.value', detalhamento)

  cy.get('body').then(($body) => {
    if ($body.find('table tbody tr').length > 0) {
      cy.get('table tbody tr').should('have.length.greaterThan', 0)
    } else {
      cy.contains('Nenhum resultado encontrado').should('be.visible')
    }
  })
})

Cypress.Commands.add('validar_filtro_conta_creditos_da_escola', () => {
  cy.get(creditos.filtrar_conta(), { timeout: 3000 })
    .find('option:selected')
    .should('contain.text', 'Cheque')

  cy.get('body').then(($body) => {
    if ($body.find('table tbody tr').length > 0) {
    } else {
      cy.contains('Nenhum resultado encontrado').should('be.visible')
    }
  })
})

Cypress.Commands.add('validar_filtro_acao_creditos_da_escola', (acao) => {
  cy.get(creditos.acao(), { timeout: 3000 })
    .find('option:selected')
    .should('contain.text', acao)

  cy.get('body').then(($body) => {
    if ($body.find('table tbody tr').length > 0) {
    } else {
      cy.contains('Nenhum resultado encontrado').should('be.visible')
    }
  })
})

Cypress.Commands.add('validar_filtro_periodo_de_creditos_da_escola', (dataDe) => {
  cy.get(creditos.filtrar_periodo_de(), { timeout: 3000 })
    .should('have.value', dataDe)
})

Cypress.Commands.add('validar_filtro_periodo_ate_creditos_da_escola', (dataAte) => {
  cy.get(creditos.filtrar_periodo_ate(), { timeout: 3000 })
    .should('have.value', dataAte)
})

Cypress.Commands.add('validar_filtros_creditos_da_escola_por_caso', (caso) => {
  switch (caso.toLowerCase()) {
    case 'detalhamento do crédito':
      cy.validar_filtro_detalhamento_credito('Fevereiro')
      break

    case 'conta':
      cy.validar_filtro_conta_creditos_da_escola('Cheque')
      break

    case 'ação':
    case 'acao':
      cy.validar_filtro_acao_creditos_da_escola('PTRF Básico')
      break

    case 'período de':
    case 'periodo de':
      cy.validar_filtro_periodo_de_creditos_da_escola('01/01/2026')
      break

    case 'período até':
    case 'periodo até':
    case 'periodo ate':
      cy.validar_filtro_periodo_ate_creditos_da_escola('31/12/2026')
      break

    default:
      throw new Error(`Caso de validação não mapeado: ${caso}`)
  }
})

Cypress.Commands.add('validar_todos_os_filtros_creditos_da_escola', (filtros = {}) => {
  const defaults = {
    detalhamento: 'Fevereiro',
    conta: 'Cheque',
    acao: 'PTRF Básico',
    dataDe: '01/01/2026',
    dataAte: '31/12/2026'
  }

  const {
    detalhamento,
    conta,
    acao,
    dataDe,
    dataAte
  } = { ...defaults, ...filtros }

  cy.get(creditos.detalhamento_credito(), { timeout: 3000 })
    .should('be.visible')
    .and('have.value', detalhamento)

  cy.get(creditos.filtrar_conta(), { timeout: 3000 })
    .should('be.visible')
    .find('option:selected')
    .should('contain.text', conta)

  cy.get(creditos.acao(), { timeout: 3000 })
    .should('be.visible')
    .find('option:selected')
    .should('contain.text', acao)

  cy.get(creditos.filtrar_periodo_de(), { timeout: 3000 })
    .should('be.visible')
    .and('have.value', dataDe)

  cy.get(creditos.filtrar_periodo_ate(), { timeout: 3000 })
    .should('be.visible')
    .and('have.value', dataAte)

cy.get('#content .lista-de-receitas-visible form .d-flex.justify-content-end button.btn-success', { timeout: 10000 })
  .should('exist')
  .click({ force: true })

  cy.contains('Nenhum resultado encontrado').should('not.exist')
})

Cypress.Commands.add('validar_botoes_creditos_ue', (botao) => {

  const seletores = {
    'limpa filtro': creditos.btn_limpar_filtro(),
    'cancela': creditos.btn_cancelar()
  }

  cy.get(creditos.mais_filtros())
    .should('be.visible')
    .click()

  const seletor = seletores[botao.toLowerCase().trim()]

  if (!seletor) {
    throw new Error(`Botão não mapeado: ${botao}`)
  }

  cy.get(seletor)
    .should('be.visible')
    .and('exist')
})

Cypress.Commands.add('validar_valores_reprogramados_ue', (botao) => {

  const seletores = {
    'valores reprogramados': creditos.btn_valores_reprogramados()
  }

  const seletor = seletores[botao]

  if (!seletor) {
    throw new Error(`Botão não mapeado: ${botao}`)
  }

  cy.get(seletor)
    .should('be.visible')
    .and('not.be.disabled')
    .click()

  cy.get(creditos.titulo_valores_reprogramados(), { timeout: 10000 })
    .should('be.visible')
})

Cypress.Commands.add('validar_soma_valores_reprogramados_ue', () => {

  const parseMoeda = (valor) => {
    if (typeof valor === 'number') return valor

    return Number(
      String(valor || 0)
        .replace('R$', '')
        .replace(/\./g, '')
        .replace(',', '.')
        .trim()
    ) || 0
  }

  const somarValoresAcoes = (acoes = []) => {
    return acoes.reduce((totais, acao) => {
      ;['custeio', 'capital', 'livre'].forEach((categoria) => {
        if (acao?.[categoria]) {
          totais.valorUe += parseMoeda(acao[categoria].valor_ue)
          totais.valorDre += parseMoeda(acao[categoria].valor_dre)
        }
      })

      return totais
    }, { valorUe: 0, valorDre: 0 })
  }

  cy.intercept(
    'GET',
    '**/api/valores-reprogramados/get-valores-reprogramados/?associacao_uuid=*'
  ).as('getValoresReprogramados')

  cy.reload()

  cy.wait('@getValoresReprogramados', { timeout: 15000 }).then(({ response }) => {
    expect(response.statusCode).to.eq(200)

    const contas = response.body?.contas || []

    expect(contas, 'Lista de contas da API').to.be.an('array').and.not.be.empty

    const totaisApi = contas.reduce((acc, item) => {
      const totaisConta = somarValoresAcoes(item?.conta?.acoes || [])
      acc.valorUe += totaisConta.valorUe
      acc.valorDre += totaisConta.valorDre
      return acc
    }, { valorUe: 0, valorDre: 0 })

    const totalUeApi = Number(totaisApi.valorUe.toFixed(2))
    const totalDreApi = Number(totaisApi.valorDre.toFixed(2))

    cy.log(`Total UE API: ${totalUeApi}`)
    cy.log(`Total DRE API: ${totalDreApi}`)

    cy.get(creditos.titulo_valores_reprogramados(), { timeout: 10000 })
      .should('be.visible')

    cy.get(creditos.tbl_total_cheque_ue(), { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((valorTela) => {
        const totalUeTela = Number(parseMoeda(valorTela).toFixed(2))
        expect(totalUeTela, 'Valor UE total na tela').to.eq(totalUeApi)
      })

    cy.get(creditos.tbl_total_cheque_dre(), { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((valorTela) => {
        const totalDreTela = Number(parseMoeda(valorTela).toFixed(2))
        expect(totalDreTela, 'Valor DRE total na tela').to.eq(totalDreApi)
      })
  })
})

Cypress.Commands.add('validar_campos_cadastrar_creditos_da_escola_ue', () => {
    cy.get(creditos.btn_cadastrar_credito(), { timeout: 3000 })
    .should('be.visible')
    .click()

    cy.get(creditos.btn_salvar_credito(), { timeout: 3000 })
    .should('be.visible')
    .click()

    cy.get(creditos.erro_salvar_credito())
    .should('to.exist')
})

Cypress.Commands.add('cadastrar_creditos_da_escola_ue', (campo) => {
  const tipoReceita = campo?.trim().toLowerCase()

  function preencherDataCredito(dataFormatada) {
    cy.get(creditos.inserir_data_credito(), { timeout: 5000 })
      .should('be.visible')
      .then(($input) => {
        cy.wrap($input)
          .click({ force: true })
          .clear({ force: true })
          .type(dataFormatada, { force: true, delay: 0 })

        cy.wrap($input).invoke('val').then((valor) => {
          if (!valor) {
            cy.wrap($input)
              .invoke('val', dataFormatada)
              .trigger('input')
              .trigger('change')
          }
        })
      })

    cy.get('body').click(0, 0, { force: true })
    cy.get('body').type('{esc}', { force: true })
  }

  function selecionarPrimeiraOpcaoValida(selector) {
    cy.get(selector, { timeout: 15000 })
      .should('be.visible')
      .should('not.be.disabled')
      .scrollIntoView()
      .find('option')
      .then(($options) => {
        const opcoesValidas = [...$options].filter((opt) => {
          const texto = opt.textContent.trim().toLowerCase()
          const valor = (opt.value || '').trim()

          return (
            valor !== '' &&
            !texto.includes('selecione') &&
            !texto.includes('selecione uma opção') &&
            !opt.disabled
          )
        })

        expect(opcoesValidas.length, `esperava ao menos uma opção válida em ${selector}`)
          .to.be.greaterThan(0)

        cy.get(selector).select(opcoesValidas[0].value, { force: true })
      })
  }

  function preencherCamposComuns() {
    selecionarPrimeiraOpcaoValida(creditos.selecionar_conta_associacao())
    selecionarPrimeiraOpcaoValida(creditos.selecionar_acao_associacao())

    cy.get(creditos.inserir_valor_credito(), { timeout: 5000 })
      .should('be.visible')
      .clear()
      .type('1', { force: true })
      .blur()

    cy.get(creditos.erro_salvar_credito(), { timeout: 5000 })
      .should('not.exist')

    cy.get('body').click(0, 0, { force: true })

    cy.get(creditos.btn_salvar_credito(), { timeout: 5000 })
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 10000 })
    .should('be.visible')
    .click()

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 10000 })
    .should('be.visible')
    .find('option')
    .should('have.length.greaterThan', 1)

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 10000 })
    .should('be.visible')
    .select(campo, { force: true })

  const hoje = new Date()
  const dia = String(hoje.getDate()).padStart(2, '0')
  const mes = String(hoje.getMonth() + 1).padStart(2, '0')
  const ano = hoje.getFullYear()
  const dataFormatada = `${dia}/${mes}/${ano}`

  preencherDataCredito(dataFormatada)

  switch (tipoReceita) {
    case 'recurso externo':
      cy.get(creditos.selecionar_detalhamento_credito_re(), { timeout: 10000 })
        .should('exist')
        .should('be.visible')
        .clear()
        .type('Teste automatizado', { force: true })
        .blur()

      preencherCamposComuns()
      break

    case 'rendimento':
      cy.get(creditos.selecionar_detalhamento_credito_rend(), { timeout: 10000 })
        .should('exist')
        .should('be.visible')
        .find('option')
        .should('have.length.greaterThan', 1)

      selecionarPrimeiraOpcaoValida(creditos.selecionar_detalhamento_credito_rend())

      preencherCamposComuns()
      break

    case 'repasse':
      cy.get(creditos.btn_selecionar_repasse(), { timeout: 10000 })
        .should('be.visible')
        .click({ force: true })

      cy.get(creditos.btn_salvar_credito(), { timeout: 5000 })
        .should('be.visible')
        .click({ force: true })

      cy.get(creditos.btn_gravar_repasse(), { timeout: 10000 })
        .should('be.visible')
        .click({ force: true })
      break

    default:
      throw new Error(`Tipo de crédito não tratado no comando: ${campo}`)
  }
})