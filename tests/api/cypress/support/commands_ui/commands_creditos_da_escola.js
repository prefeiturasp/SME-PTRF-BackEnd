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

  const seletorFn = mapaCampos[campo]

  if (!seletorFn) {
    throw new Error(`Campo "${campo}" não mapeado`)
  }

  const seletor = seletorFn()

  cy.get('.table > tbody > tr', { timeout: 20000 })
    .should('exist')
    .should('have.length.greaterThan', 0)

  // valida se o elemento existe antes de tentar usar
  cy.get('body').then(($body) => {
    if ($body.find(seletor).length === 0) {
      throw new Error(`Elemento do campo "${campo}" não encontrado: ${seletor}`)
    }
  })

  cy.get(seletor, { timeout: 10000 })
    .should('be.visible')
    .invoke('text')
    .then((texto) => {
      expect(texto.trim(), `Campo "${campo}" vazio`).to.not.eq('')
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

      cy.get(creditos.tbl_sem_filtros_aplicados(), { timeout: 15000 })
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

  cy.get(creditos.filtrar_por(), { timeout: 30000 })
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

  cy.get(creditos.filtrar_por(), { timeout: 30000 })
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
  cy.get(creditos.mais_filtros(), { timeout: 30000 })
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

  cy.get(creditos.mais_filtros(), { timeout: 15000 })
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

  cy.get(seletor, { timeout: 15000 })
    .should('be.visible')
    .and('not.be.disabled')
    .click()

  cy.get(creditos.titulo_valores_reprogramados(), { timeout: 15000 })
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
    cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

    cy.get(creditos.btn_salvar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

    cy.get(creditos.erro_salvar_credito())
    .should('to.exist')
})

Cypress.Commands.add('cadastrar_creditos_da_escola_ue', (campo) => {
  const tipoReceita = String(campo).trim().toLowerCase()

  function preencherDataCredito(dataFormatada) {
    cy.get(creditos.inserir_data_credito(), { timeout: 5000 })
      .should('be.visible')
      .clear({ force: true })
      .type(dataFormatada, { force: true })
      .blur({ force: true })

    cy.get('body').type('{esc}', { force: true })
  }

  function selecionarPrimeiraOpcaoValida(selector) {
    cy.get(selector, { timeout: 10000 })
      .should('be.visible')
      .find('option')
      .then(($options) => {
        const opcaoValida = [...$options].find((opt) => {
          const texto = (opt.textContent || '').trim().toLowerCase()
          const valor = (opt.value || '').trim()

          return (
            valor !== '' &&
            !opt.disabled &&
            !texto.includes('selecione')
          )
        })

        expect(opcaoValida, `Nenhuma opção válida encontrada em ${selector}`).to.exist
        cy.get(selector).select(opcaoValida.value, { force: true })
      })
  }

  function clicarSalvarCredito() {
    cy.get(creditos.btn_salvar_credito(), { timeout: 10000 })
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })
  }

  function preencherCamposComuns() {
    selecionarPrimeiraOpcaoValida(creditos.selecionar_conta_associacao())
    selecionarPrimeiraOpcaoValida(creditos.selecionar_acao_associacao())

    cy.get(creditos.inserir_valor_credito(), { timeout: 5000 })
      .should('be.visible')
      .clear()
      .type('1', { force: true })
      .blur({ force: true })

    cy.get(creditos.erro_salvar_credito(), { timeout: 5000 })
      .should('not.exist')

    clicarSalvarCredito()
  }

  function processarFluxoRepasse() {
    cy.get('body').then(($body) => {
      const textoTela = $body.text()

      if (textoTela.includes('No momento não existem repasses pendentes para a associação.')) {
        cy.get(creditos.btn_cancelar_sem_repasse(), { timeout: 5000 })
          .should('be.visible')
          .click({ force: true })
        return
      }

      const btnRepasse = $body.find(creditos.btn_selecionar_repasse())

      if (!btnRepasse.length) {
        cy.log('Botão de repasse não encontrado')
        return
      }

      cy.wrap(btnRepasse.first()).click({ force: true })
    })

    clicarSalvarCredito()

    cy.get('body').then(($body) => {
      const textoTela = $body.text()

      if (textoTela.includes('No momento não existem repasses pendentes para a associação.')) {
        cy.get(creditos.btn_cancelar_sem_repasse(), { timeout: 5000 })
          .should('be.visible')
          .click({ force: true })
        return
      }

      const btnGravar = $body.find(creditos.btn_gravar_repasse())

      if (btnGravar.length) {
        cy.wrap(btnGravar.first())
          .should('not.be.disabled')
          .click({ force: true })
      }
    })
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click({ force: true })

  cy.url().should('include', '/cadastro-de-credito')

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 30000 })
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
        .should('be.visible')
        .clear()
        .type('Teste automatizado', { force: true })
        .blur({ force: true })

      preencherCamposComuns()
      break

    case 'rendimento':
      selecionarPrimeiraOpcaoValida(creditos.selecionar_detalhamento_credito_rend())
      preencherCamposComuns()
      break

    case 'repasse':
      processarFluxoRepasse()
      break

    default:
      throw new Error(`Tipo de crédito não tratado: ${campo}`)
  }
})

Cypress.Commands.add('cadastrar_devolucao_creditos_da_escola_ue', () => {
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
    cy.get('body').then(($body) => {
      if ($body.find(selector).length) {
        cy.get(selector, { timeout: 15000 })
          .should('exist')
          .should('be.visible')
          .should('not.be.disabled')
          .scrollIntoView()
          .find('option')
          .then(($options) => {
            const opcoesValidas = [...$options].filter((opt) => {
              const texto = (opt.textContent || '').trim().toLowerCase()
              const valor = (opt.value || '').trim()

              return (
                valor !== '' &&
                !texto.includes('selecione') &&
                !texto.includes('selecione uma opção') &&
                !opt.disabled
              )
            })

            if (opcoesValidas.length > 0) {
              cy.get(selector).select(opcoesValidas[0].value, { force: true })
            } else {
              cy.log(`Nenhuma opção válida encontrada em ${selector}`)
            }
          })
      } else {
        cy.log(`Campo ${selector} não disponível neste fluxo`)
      }
    })
  }

  function selecionarOpcaoPorTexto(selector, textoOpcao) {
    cy.get(selector, { timeout: 15000 })
      .should('exist')
      .should('be.visible')
      .should('not.be.disabled')
      .select(textoOpcao, { force: true })

    cy.get(selector)
      .find('option:selected')
      .should(($selected) => {
        const textoSelecionado = $selected.text().trim().toLowerCase()
        expect(textoSelecionado).to.contain(textoOpcao.trim().toLowerCase())
      })
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

  selecionarOpcaoPorTexto(creditos.selecionar_tipo_receita(), 'Devolução à conta')

  cy.get('body', { timeout: 15000 }).should('be.visible')

  cy.get(creditos.selecionar_detalhamento_credito_rend(), { timeout: 15000 })
    .should('exist')
    .should('be.visible')

  selecionarPrimeiraOpcaoValida(creditos.selecionar_detalhamento_credito_rend())

  // Campo de período de referência pode não existir em alguns fluxos
  selecionarPrimeiraOpcaoValida(creditos.selecionar_periodo_referencia_credito())

  const hoje = new Date()
  const dia = String(hoje.getDate()).padStart(2, '0')
  const mes = String(hoje.getMonth() + 1).padStart(2, '0')
  const ano = hoje.getFullYear()
  const dataFormatada = `${dia}/${mes}/${ano}`

  preencherDataCredito(dataFormatada)

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
})

Cypress.Commands.add('cadastrar_credito_ue', () => {
  const timestamp = Date.now()
  const nomeTeste = `Teste automatizado ${timestamp}`

  Cypress.env('CREDITO_UE', nomeTeste)

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
      .find('option')
      .then(($options) => {
        const opcoesValidas = [...$options].filter((opt) => {
          const texto = opt.textContent.trim().toLowerCase()
          const valor = (opt.value || '').trim()

          return (
            valor !== '' &&
            !texto.includes('selecione') &&
            !opt.disabled
          )
        })

        expect(opcoesValidas.length, `esperava ao menos uma opção válida em ${selector}`)
          .to.be.greaterThan(0)

        const valorSelecionado = opcoesValidas[0].value

        cy.get(selector)
          .select(valorSelecionado, { force: true })
          .should('have.value', valorSelecionado)
      })
  }

  function preencherCampos() {
    selecionarPrimeiraOpcaoValida(creditos.selecionar_conta_associacao())
    selecionarPrimeiraOpcaoValida(creditos.selecionar_acao_associacao())

    cy.get(creditos.inserir_valor_credito(), { timeout: 5000 })
      .should('be.visible')
      .clear()
      .type('1', { force: true })
      .blur()

    cy.get(creditos.btn_salvar_credito(), { timeout: 10000 })
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })

    cy.url({ timeout: 10000 }).should('include', '/lista-de-receitas')
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 30000 })
    .should('be.visible')
    .select('Recurso Externo', { force: true })

  const hoje = new Date()
  const dataFormatada = `${String(hoje.getDate()).padStart(2, '0')}/${String(hoje.getMonth() + 1).padStart(2, '0')}/${hoje.getFullYear()}`

  preencherDataCredito(dataFormatada)

  cy.get(creditos.selecionar_detalhamento_credito_re(), { timeout: 15000 })
    .should('be.visible')
    .clear()
    .type(nomeTeste, { force: true })
    .should('have.value', nomeTeste)

  preencherCampos()

  return cy.wrap(nomeTeste)
})

Cypress.Commands.add('excluir_credito_ue', () => {
  const timestamp = Date.now()
  const nomeTeste = `Teste automatizado ${timestamp}`

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
      .find('option')
      .then(($options) => {
        const opcoesValidas = [...$options].filter((opt) => {
          const texto = opt.textContent.trim().toLowerCase()
          const valor = (opt.value || '').trim()

          return (
            valor !== '' &&
            !texto.includes('selecione') &&
            !opt.disabled
          )
        })

        expect(opcoesValidas.length).to.be.greaterThan(0)

        const valorSelecionado = opcoesValidas[0].value

        cy.get(selector)
          .select(valorSelecionado, { force: true })
          .should('have.value', valorSelecionado)
      })
  }

  function tratarPeriodoFechado() {
    cy.get('body').then(($body) => {
      const textoTela = $body.text()

      if (textoTela.includes('Período Fechado')) {
        cy.get('body > div.fade.modal.show > div > div > div.modal-footer > button', { timeout: 10000 })
          .should('be.visible')
          .click({ force: true })
      }
    })
  }

  function preencherCampos() {
    selecionarPrimeiraOpcaoValida(creditos.selecionar_conta_associacao())
    selecionarPrimeiraOpcaoValida(creditos.selecionar_acao_associacao())

    cy.get(creditos.inserir_valor_credito(), { timeout: 30000 })
      .should('be.visible')
      .clear()
      .type('1', { force: true })
      .blur()

    cy.get(creditos.btn_salvar_credito(), { timeout: 30000 })
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })

    tratarPeriodoFechado()

    cy.url({ timeout: 30000 }).should('include', '/lista-de-receitas')
  }

  function aguardarToast() {
    cy.get('body').then(($body) => {
      if ($body.find('.Toastify__toast').length > 0) {
        cy.get('.Toastify__toast', { timeout: 30000 }).should('not.exist')
      }
    })
  }

  function selecionarRegistroParaExcluir() {
    cy.get(creditos.selecionar_recurso_credito_ue(), { timeout: 30000 })
      .should('exist')
      .should('be.visible')
      .click({ force: true })

    cy.get('body').then(($body) => {
      const botaoExiste = $body.find(creditos.btn_deletar_credito_ue()).length > 0

      if (!botaoExiste) {
        cy.get(creditos.selecionar_recurso_credito_ue(), { timeout: 30000 })
          .dblclick({ force: true })
      }
    })

    cy.get(creditos.btn_deletar_credito_ue(), { timeout: 30000 })
      .should('exist')
      .should('be.visible')
      .should('not.be.disabled')
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 30000 })
    .should('be.visible')
    .select('Recurso Externo', { force: true })

  const hoje = new Date()
  const dataFormatada = `${String(hoje.getDate()).padStart(2, '0')}/${String(hoje.getMonth() + 1).padStart(2, '0')}/${hoje.getFullYear()}`

  preencherDataCredito(dataFormatada)

  cy.get(creditos.selecionar_detalhamento_credito_re(), { timeout: 30000 })
    .should('be.visible')
    .clear()
    .type(nomeTeste, { force: true })

  preencherCampos()
  aguardarToast()
  selecionarRegistroParaExcluir()

  cy.get(creditos.btn_deletar_credito_ue(), { timeout: 30000 })
    .should('be.visible')
    .click({ force: true })

  cy.get(creditos.btn_excluir_credito_ue(), { timeout: 30000 })
    .should('be.visible')
    .click({ force: true })

  cy.get(creditos.btn_excluir_credito_ue(), { timeout: 30000 })
    .should('not.exist')
})

Cypress.Commands.add('validar_credito_ue', () => {
  cy.get(creditos.titulo_valores_reprogramados(), { timeout: 30000 })
    .should('be.visible')
})

Cypress.Commands.add('editar_credito_ue', () => {
  const timestamp = Date.now()
  const nomeTeste = `Teste automatizado ${timestamp}`

  function preencherDataCredito(dataFormatada) {
    cy.get(creditos.inserir_data_credito(), { timeout: 30000 })
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
      .find('option')
      .then(($options) => {
        const opcoesValidas = [...$options].filter((opt) => {
          const texto = opt.textContent.trim().toLowerCase()
          const valor = (opt.value || '').trim()

          return (
            valor !== '' &&
            !texto.includes('selecione') &&
            !opt.disabled
          )
        })

        expect(opcoesValidas.length).to.be.greaterThan(0)

        const valorSelecionado = opcoesValidas[0].value

        cy.get(selector)
          .select(valorSelecionado, { force: true })
          .should('have.value', valorSelecionado)
      })
  }

  function tratarPeriodoFechado() {
    cy.get('body').then(($body) => {
      const textoTela = $body.text()

      if (textoTela.includes('Período Fechado')) {
        cy.get('body > div.fade.modal.show > div > div > div.modal-footer > button', { timeout: 10000 })
          .should('be.visible')
          .click({ force: true })
      }
    })
  }

  function preencherCampos() {
    selecionarPrimeiraOpcaoValida(creditos.selecionar_conta_associacao())
    selecionarPrimeiraOpcaoValida(creditos.selecionar_acao_associacao())

    cy.get(creditos.inserir_valor_credito(), { timeout: 5000 })
      .should('be.visible')
      .clear()
      .type('1', { force: true })
      .blur()

    cy.get(creditos.btn_salvar_credito(), { timeout: 30000 })
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })

    tratarPeriodoFechado()
    cy.url({ timeout: 30000 }).should('include', '/lista-de-receitas')
  }

  function aguardarToast() {
    cy.get('body').then(($body) => {
      if ($body.find('.Toastify__toast').length > 0) {
        cy.get('.Toastify__toast', { timeout: 30000 }).should('not.exist')
      }
    })
  }

  function selecionarPrimeiroRegistroDaListagem() {
    cy.url({ timeout: 30000 }).should('include', '/lista-de-receitas')

    cy.get(creditos.selecionar_recurso_credito_ue(), { timeout: 30000 })
      .should('exist')
      .should('be.visible')
      .first()
      .click({ force: true })

    cy.url({ timeout: 30000 }).should('include', '/edicao-de-receita/')
    cy.get(creditos.btn_salvar_credito(), { timeout: 30000 })
      .should('exist')
      .should('be.visible')
  }

  function voltarParaListagemSeEstiverEmEdicao() {
    cy.url({ timeout: 30000 }).then((urlAtual) => {
      if (urlAtual.includes('/edicao-de-receita/')) {
        cy.go('back')
      }
    })

    cy.url({ timeout: 15000 }).should('include', '/lista-de-receitas')
  }

  function reabrirPrimeiroRegistroDaListagem() {
    voltarParaListagemSeEstiverEmEdicao()
    aguardarToast()

    cy.get(creditos.selecionar_recurso_credito_ue(), { timeout: 15000 })
      .should('exist')
      .should('be.visible')
      .first()
      .click({ force: true })

    cy.url({ timeout: 10000 }).should('include', '/edicao-de-receita/')
    cy.get(creditos.btn_salvar_credito(), { timeout: 15000 })
      .should('exist')
      .should('be.visible')
  }

  function excluirRegistroAberto() {
    cy.get(creditos.btn_deletar_credito_ue(), { timeout: 15000 })
      .should('exist')
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })

    cy.get(creditos.btn_excluir_credito_ue(), { timeout: 15000 })
      .should('exist')
      .should('be.visible')
      .should('not.be.disabled')
      .click({ force: true })

    cy.get(creditos.btn_excluir_credito_ue(), { timeout: 15000 })
      .should('not.exist')
  }

  cy.get(creditos.btn_cadastrar_credito(), { timeout: 30000 })
    .should('be.visible')
    .click()

  cy.get(creditos.selecionar_tipo_receita(), { timeout: 30000 })
    .should('be.visible')
    .select('Recurso Externo', { force: true })

  const hoje = new Date()
  const dataFormatada = `${String(hoje.getDate()).padStart(2, '0')}/${String(hoje.getMonth() + 1).padStart(2, '0')}/${hoje.getFullYear()}`

  preencherDataCredito(dataFormatada)

  cy.get(creditos.selecionar_detalhamento_credito_re(), { timeout: 30000 })
    .should('be.visible')
    .clear()
    .type(nomeTeste, { force: true })

  preencherCampos()
  aguardarToast()

  selecionarPrimeiroRegistroDaListagem()

  cy.get(creditos.btn_salvar_credito(), { timeout: 10000 })
    .should('be.visible')
    .should('not.be.disabled')
    .click({ force: true })

  tratarPeriodoFechado()
  aguardarToast()

  reabrirPrimeiroRegistroDaListagem()

  excluirRegistroAberto()
})