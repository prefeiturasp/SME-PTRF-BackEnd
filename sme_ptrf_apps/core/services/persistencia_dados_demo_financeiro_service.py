import logging
from sme_ptrf_apps.core.models import (
    DadosDemonstrativoFinanceiro,
    ItemResumoPorAcao,
    ItemCredito,
    ItemDespesa,
    CategoriaDespesaChoices,
    InformacaoDespesaChoices
)
from datetime import datetime
import decimal

logger = logging.getLogger(__name__)


class PersistenciaDadosDemoFinanceiro:
    def __init__(self, dados, demonstrativo):
        self.demonstrativo = demonstrativo
        self.dados = dados

        # Cria registro apenas com informação do demonstrativo vinculado
        self.registro = self.cria_novo_registro()

        # Cabecalho
        self.cria_cabecalho()

        # Bloco 1
        self.cria_identificacao_associacao()

        # Bloco 2
        self.cria_identificacao_bancaria()

        # bloco 3
        self.cria_registros_resumo_por_acao()

        # bloco 4
        self.cria_registros_creditos()

        # Bloco 5
        self.cria_registros_despesas_demonstradas()

        # Bloco 6
        self.cria_registros_despesas_nao_demonstradas()

        # Bloco 7
        self.cria_registros_despesas_nao_demonstradas_periodos_anteriores()

        # Bloco 8
        self.cria_registro_justificativa_info_adicionais()

        # Bloco 9
        self.cria_registro_assinatura_responsaveis()

        # Rodape
        self.cria_rodape()

    @staticmethod
    def string_to_date(date_str):
        if date_str:
            try:
                date_format = '%d/%m/%Y'
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj
            except ValueError:
                return None
        return None

    @staticmethod
    def formata_valor(valor):
        if valor:
            try:
                from babel.numbers import format_currency
                sinal, valor_formatado = format_currency(valor, 'BRL', locale='pt_BR').split('\xa0')
                sinal = '-' if '-' in sinal else ''

                return f'{sinal}{valor_formatado}'
            except decimal.InvalidOperation as err:
                logger.error(f'Erro ao converter o valor: {valor} -  {err}')

        return 0

    @staticmethod
    def dict_list_to_text(dict_list, key):
        text = ''
        for item in dict_list:
            text = text + f"{item[key]}\r\n"

        return text

    def retorna_categoria_rateio_despesa_imposto(self, despesa_imposto):
        uuids_rateios_despesas_demonstradas = [r["uuid_rateio"] for r in self.dados['despesas_demonstradas']['linhas']]
        uuids_rateios_despesas_nao_demonstradas = [r["uuid_rateio"] for r in self.dados['despesas_nao_demonstradas']['linhas']]
        uuids_rateios_despesas_nao_demonstradas_periodos_anteriores = [r["uuid_rateio"] for r in self.dados['despesas_anteriores_nao_demonstradas']['linhas']]

        if despesa_imposto["uuid_rateio_imposto"] in uuids_rateios_despesas_demonstradas:
            return CategoriaDespesaChoices.DEMONSTRADA
        elif despesa_imposto["uuid_rateio_imposto"] in uuids_rateios_despesas_nao_demonstradas:
            return CategoriaDespesaChoices.NAO_DEMONSTRADA
        elif despesa_imposto["uuid_rateio_imposto"] in uuids_rateios_despesas_nao_demonstradas_periodos_anteriores:
            return CategoriaDespesaChoices.NAO_DEMONSTRADA_PERIODO_ANTERIOR

    def exclui_registro_existente(self):
        registro_existente = DadosDemonstrativoFinanceiro.objects.filter(demonstrativo=self.demonstrativo).all()

        for registro in registro_existente:
            registro.delete()

    def cria_novo_registro(self):

        self.exclui_registro_existente()

        novo_registro = DadosDemonstrativoFinanceiro.objects.create(
            demonstrativo=self.demonstrativo,
        )

        return novo_registro

    def cria_cabecalho(self):
        periodo_referencia = self.dados['cabecalho']['periodo_referencia']
        periodo_data_inicio = self.string_to_date(self.dados['cabecalho']['periodo_data_inicio'])
        periodo_data_fim = self.string_to_date(self.dados['cabecalho']['periodo_data_fim'])
        conta_associacao = self.dados['cabecalho']['conta']

        self.registro.periodo_referencia = periodo_referencia
        self.registro.periodo_data_inicio = periodo_data_inicio
        self.registro.periodo_data_fim = periodo_data_fim
        self.registro.conta_associacao = conta_associacao

        self.registro.save()

    def cria_identificacao_associacao(self):
        nome_associacao = self.dados['identificacao_apm']['nome_associacao']
        cnpj_associacao = self.dados['identificacao_apm']['cnpj_associacao']
        nome_dre_associacao = self.dados['identificacao_apm']['nome_dre_associacao']
        codigo_eol_associacao = self.dados['identificacao_apm']['codigo_eol_associacao']

        self.registro.nome_associacao = nome_associacao
        self.registro.cnpj_associacao = cnpj_associacao
        self.registro.nome_dre_associacao = nome_dre_associacao
        self.registro.codigo_eol_associacao = codigo_eol_associacao

        self.registro.save()

    def cria_identificacao_bancaria(self):
        banco = self.dados['identificacao_conta']['banco']
        agencia = self.dados['identificacao_conta']['agencia']
        conta = self.dados['identificacao_conta']['conta']
        data_extrato = self.string_to_date(self.dados['identificacao_conta']['data_extrato'])
        saldo_extrato = self.dados['identificacao_conta']['saldo_extrato']
        conta_encerrada_em = self.dados['identificacao_conta']['encerrada_em']

        self.registro.banco = banco
        self.registro.agencia = agencia
        self.registro.conta = conta
        self.registro.data_extrato = data_extrato
        self.registro.saldo_extrato = saldo_extrato
        self.registro.conta_encerrada_em = conta_encerrada_em

        self.registro.save()

    def cria_registros_resumo_por_acao(self):
        for item in self.dados['resumo_por_acao']['resumo_acoes']:
            acao_associacao = item["acao_associacao"]

            custeio_saldo_anterior = item["linha_custeio"]["saldo_anterior"]
            custeio_credito = item["linha_custeio"]["credito"]
            custeio_despesa_realizada = item["linha_custeio"]["despesa_realizada"]
            custeio_despesa_nao_realizada = item["linha_custeio"]["despesa_nao_realizada"]
            custeio_saldo_reprogramado_proximo = item["linha_custeio"]["saldo_reprogramado_proximo"]
            custeio_despesa_nao_demostrada_outros_periodos = item["linha_custeio"]["despesa_nao_demostrada_outros_periodos"]
            custeio_valor_saldo_bancario_custeio = item["linha_custeio"]["valor_saldo_bancario_custeio"]

            livre_saldo_anterior = item["linha_livre"]["saldo_anterior"]
            livre_credito = item["linha_livre"]["credito"]
            livre_saldo_reprogramado_proximo = item["linha_livre"]["saldo_reprogramado_proximo"]
            livre_valor_saldo_reprogramado_proximo_periodo = item["linha_livre"]["valor_saldo_reprogramado_proximo_periodo_livre"]

            capital_saldo_anterior = item["linha_capital"]["saldo_anterior"]
            capital_credito = item["linha_capital"]["credito"]
            capital_despesa_realizada = item["linha_capital"]["despesa_realizada"]
            capital_despesa_nao_realizada = item["linha_capital"]["despesa_nao_realizada"]
            capital_saldo_reprogramado_proximo = item["linha_capital"]["saldo_reprogramado_proximo"]
            capital_despesa_nao_demostrada_outros_periodos = item["linha_capital"]["despesa_nao_demostrada_outros_periodos"]
            capital_valor_saldo_bancario_capital = item["linha_capital"]["valor_saldo_bancario_capital"]

            total_valores = item["total_valores"]
            saldo_bancario = item["saldo_bancario"]

            ItemResumoPorAcao.objects.create(
                dados_demonstrativo=self.registro,
                acao_associacao=acao_associacao,
                custeio_saldo_anterior=custeio_saldo_anterior,
                custeio_credito=custeio_credito,
                custeio_despesa_realizada=custeio_despesa_realizada,
                custeio_despesa_nao_realizada=custeio_despesa_nao_realizada,
                custeio_saldo_reprogramado_proximo=custeio_saldo_reprogramado_proximo,
                custeio_despesa_nao_demostrada_outros_periodos=custeio_despesa_nao_demostrada_outros_periodos,
                custeio_valor_saldo_bancario_custeio=custeio_valor_saldo_bancario_custeio,
                livre_saldo_anterior=livre_saldo_anterior,
                livre_credito=livre_credito,
                livre_saldo_reprogramado_proximo=livre_saldo_reprogramado_proximo,
                livre_valor_saldo_reprogramado_proximo_periodo=livre_valor_saldo_reprogramado_proximo_periodo,
                capital_saldo_anterior=capital_saldo_anterior,
                capital_credito=capital_credito,
                capital_despesa_realizada=capital_despesa_realizada,
                capital_despesa_nao_realizada=capital_despesa_nao_realizada,
                capital_saldo_reprogramado_proximo=capital_saldo_reprogramado_proximo,
                capital_despesa_nao_demostrada_outros_periodos=capital_despesa_nao_demostrada_outros_periodos,
                capital_valor_saldo_bancario_capital=capital_valor_saldo_bancario_capital,
                total_valores=total_valores,
                saldo_bancario=saldo_bancario
            )

        totais_gerais = self.dados['resumo_por_acao']["total_valores"]

        custeio_total_geral_saldo_anterior = totais_gerais["saldo_anterior"]["C"]
        custeio_total_geral_credito = totais_gerais["credito"]["C"]
        custeio_total_geral_despesa_realizada = totais_gerais["despesa_realizada"]["C"]
        custeio_total_geral_despesa_nao_realizada = totais_gerais["despesa_nao_realizada"]["C"]
        custeio_total_geral_saldo_reprogramado_proximo = totais_gerais["saldo_reprogramado_proximo"]["C"]
        custeio_total_geral_despesa_nao_demostrada_outros_periodos = totais_gerais["despesa_nao_demostrada_outros_periodos"]["C"]
        custeio_total_geral_valor_saldo_bancario = totais_gerais["valor_saldo_bancario"]["C"]

        livre_total_geral_saldo_anterior = totais_gerais["saldo_anterior"]["L"]
        livre_total_geral_credito = totais_gerais["credito"]["L"]
        livre_total_geral_saldo_reprogramado_proximo = totais_gerais["saldo_reprogramado_proximo"]["L"]
        livre_total_geral_saldo_final_periodo = totais_gerais["saldo_reprogramado_proximo"]["L"]

        capital_total_geral_saldo_anterior = totais_gerais["saldo_anterior"]["K"]
        capital_total_geral_credito = totais_gerais["credito"]["K"]
        capital_total_geral_despesa_realizada = totais_gerais["despesa_realizada"]["K"]
        capital_total_geral_despesa_nao_realizada = totais_gerais["despesa_nao_realizada"]["K"]
        capital_total_geral_saldo_reprogramado_proximo = totais_gerais["saldo_reprogramado_proximo"]["K"]
        capital_total_geral_despesa_nao_demostrada_outros_periodos = totais_gerais["despesa_nao_demostrada_outros_periodos"]["K"]
        capital_total_geral_valor_saldo_bancario = totais_gerais["valor_saldo_bancario"]["K"]

        total_geral_total_valores = totais_gerais["total_valores"]
        total_geral_saldo_bancario = totais_gerais["saldo_bancario"]

        ItemResumoPorAcao.objects.create(
            dados_demonstrativo=self.registro,
            total_geral=True,
            acao_associacao="TOTAL GERAL***",
            custeio_saldo_anterior=custeio_total_geral_saldo_anterior,
            custeio_credito=custeio_total_geral_credito,
            custeio_despesa_realizada=custeio_total_geral_despesa_realizada,
            custeio_despesa_nao_realizada=custeio_total_geral_despesa_nao_realizada,
            custeio_saldo_reprogramado_proximo=custeio_total_geral_saldo_reprogramado_proximo,
            custeio_despesa_nao_demostrada_outros_periodos=custeio_total_geral_despesa_nao_demostrada_outros_periodos,
            custeio_valor_saldo_bancario_custeio=custeio_total_geral_valor_saldo_bancario,
            livre_saldo_anterior=livre_total_geral_saldo_anterior,
            livre_credito=livre_total_geral_credito,
            livre_saldo_reprogramado_proximo=livre_total_geral_saldo_reprogramado_proximo,
            livre_valor_saldo_reprogramado_proximo_periodo=livre_total_geral_saldo_final_periodo,
            capital_saldo_anterior=capital_total_geral_saldo_anterior,
            capital_credito=capital_total_geral_credito,
            capital_despesa_realizada=capital_total_geral_despesa_realizada,
            capital_despesa_nao_realizada=capital_total_geral_despesa_nao_realizada,
            capital_saldo_reprogramado_proximo=capital_total_geral_saldo_reprogramado_proximo,
            capital_despesa_nao_demostrada_outros_periodos=capital_total_geral_despesa_nao_demostrada_outros_periodos,
            capital_valor_saldo_bancario_capital=capital_total_geral_valor_saldo_bancario,
            total_valores=total_geral_total_valores,
            saldo_bancario=total_geral_saldo_bancario
        )

    def cria_registros_creditos(self):
        for receita in self.dados["creditos_demonstrados"]["linhas"]:
            tipo_receita = receita["tipo_receita"]
            detalhamento = receita["detalhamento"]
            nome_acao = receita["nome_acao"]
            data = self.string_to_date(receita["data"])
            valor = receita["valor"]

            eh_estorno = receita["eh_estorno"]
            data_estorno = self.string_to_date(receita["estorno"]["data_estorno"]) if eh_estorno else None
            numero_documento_despesa = receita["estorno"]["numero_documento_despesa"] if eh_estorno else None
            motivos_estorno_list = receita["estorno"]["motivos_estorno"] if eh_estorno else []
            motivos_estorno = self.dict_list_to_text(dict_list=motivos_estorno_list, key='motivo')
            outros_motivos_estorno = receita["estorno"]["outros_motivos_estorno"] if eh_estorno else None

            ItemCredito.objects.create(
                dados_demonstrativo=self.registro,
                tipo_receita=tipo_receita,
                detalhamento=detalhamento,
                nome_acao=nome_acao,
                data=data,
                valor=valor,
                receita_estornada=eh_estorno,
                data_estorno=data_estorno,
                numero_documento_despesa=numero_documento_despesa,
                motivos_estorno=motivos_estorno,
                outros_motivos_estorno=outros_motivos_estorno
            )

        valor_total = self.dados["creditos_demonstrados"]["valor_total"]
        self.registro.total_creditos = valor_total
        self.registro.save()

    def cria_registros_despesas(self, lista_despesas, categoria_despesa):
        for despesa in lista_despesas:
            uuid_despesa_referencia = despesa["uuid_despesa"]
            uuid_rateio_referencia = despesa["uuid_rateio"]
            razao_social = despesa["razao_social"]
            cnpj_cpf = despesa["cnpj_cpf"]
            tipo_documento = despesa["tipo_documento"]
            numero_documento = despesa["numero_documento"]
            data_documento = self.string_to_date(despesa["data_documento"])
            nome_acao_documento = despesa["nome_acao_documento"]
            especificacao_material = despesa["especificacao_material"]
            tipo_despesa = despesa["tipo_despesa"]
            tipo_transacao = despesa["tipo_transacao"]
            data_transacao = self.string_to_date(despesa["data_transacao"])
            valor = despesa["valor"]
            valor_total = despesa["valor_total"]

            if not ItemDespesa.objects.filter(uuid_rateio_referencia=uuid_rateio_referencia).filter(categoria_despesa=categoria_despesa).exists():
                item_criado = ItemDespesa.objects.create(
                    dados_demonstrativo=self.registro,
                    categoria_despesa=categoria_despesa,
                    uuid_despesa_referencia=uuid_despesa_referencia,
                    uuid_rateio_referencia=uuid_rateio_referencia,
                    razao_social=razao_social,
                    cnpj_cpf=cnpj_cpf,
                    tipo_documento=tipo_documento,
                    numero_documento=numero_documento,
                    data_documento=data_documento,
                    nome_acao_documento=nome_acao_documento,
                    especificacao_material=especificacao_material,
                    tipo_despesa=tipo_despesa,
                    tipo_transacao=tipo_transacao,
                    data_transacao=data_transacao,
                    valor=valor,
                    valor_total=valor_total
                )

                lista_despesas_imposto = []
                if 'despesas_impostos' in despesa:
                    item_criado.info_despesa = InformacaoDespesaChoices.GEROU_IMPOSTOS

                    for imposto in despesa['despesas_impostos']:
                        uuid_despesa_imposto_referencia = imposto["uuid_despesa_imposto"]
                        uuid_rateio_despesa_imposto_referencia = imposto["uuid_rateio_imposto"]
                        tipo_documento_imposto = imposto["tipo_documento"]
                        data_transacao_imposto = self.string_to_date(imposto["data_transacao"])
                        data_documento_imposto = self.string_to_date(imposto["data_documento_imposto"])
                        nome_acao_documento_imposto = imposto["nome_acao_documento"]
                        especificacao_material_imposto = imposto["especificacao_material"]
                        tipo_despesa_imposto = imposto["tipo_despesa"]
                        tipo_transacao_imposto = imposto["tipo_transacao"]
                        valor_imposto = imposto["valor"]

                        despesa_imposto_criada = ItemDespesa.objects.create(
                            dados_demonstrativo=self.registro,
                            categoria_despesa=self.retorna_categoria_rateio_despesa_imposto(imposto),
                            info_despesa=InformacaoDespesaChoices.IMPOSTO_GERADO,
                            uuid_despesa_referencia=uuid_despesa_imposto_referencia,
                            uuid_rateio_referencia=uuid_rateio_despesa_imposto_referencia,
                            tipo_documento=tipo_documento_imposto,
                            nome_acao_documento=nome_acao_documento_imposto,
                            especificacao_material=especificacao_material_imposto,
                            tipo_despesa=tipo_despesa_imposto,
                            tipo_transacao=tipo_transacao_imposto,
                            data_transacao=data_transacao_imposto,
                            data_documento=data_documento_imposto,
                            valor=valor_imposto,
                            valor_total=valor_imposto,
                        )

                        lista_despesas_imposto.append(despesa_imposto_criada.id)

                item_criado.despesas_impostos.set(lista_despesas_imposto)
                item_criado.save()

    def cria_registros_despesas_demonstradas(self):
        self.cria_registros_despesas(
            lista_despesas=self.dados["despesas_demonstradas"]["linhas"],
            categoria_despesa=CategoriaDespesaChoices.DEMONSTRADA
        )

        self.registro.total_despesas_demonstradas = self.dados["despesas_demonstradas"]["valor_total"]
        self.registro.save()

    def cria_registros_despesas_nao_demonstradas(self):
        self.cria_registros_despesas(
            lista_despesas=self.dados["despesas_nao_demonstradas"]["linhas"],
            categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA
        )

        self.registro.total_despesas_nao_demonstradas = self.dados["despesas_nao_demonstradas"]["valor_total"]
        self.registro.save()

    def cria_registros_despesas_nao_demonstradas_periodos_anteriores(self):
        self.cria_registros_despesas(
            lista_despesas=self.dados["despesas_anteriores_nao_demonstradas"]["linhas"],
            categoria_despesa=CategoriaDespesaChoices.NAO_DEMONSTRADA_PERIODO_ANTERIOR
        )

        self.registro.total_despesas_nao_demonstradas_periodos_anteriores = self.dados["despesas_anteriores_nao_demonstradas"]["valor_total"]
        self.registro.save()

    def cria_registro_justificativa_info_adicionais(self):
        self.registro.justificativa_info_adicionais = self.dados['justificativas']
        self.registro.save()

    def cria_registro_assinatura_responsaveis(self):
        cargo_substituto_presidente_ausente = self.dados["identificacao_apm"]["cargo_substituto_presidente_ausente"]
        presidente_diretoria_executiva = self.dados["identificacao_apm"]["presidente_diretoria_executiva"]
        presidente_conselho_fiscal = self.dados["identificacao_apm"]["presidente_conselho_fiscal"]

        self.registro.cargo_substituto_presidente_ausente = cargo_substituto_presidente_ausente
        self.registro.presidente_diretoria_executiva = presidente_diretoria_executiva
        self.registro.presidente_conselho_fiscal = presidente_conselho_fiscal

        self.registro.save()

    def cria_rodape(self):
        tipo_unidade = self.dados['identificacao_apm']['tipo_unidade']
        nome_unidade = self.dados['identificacao_apm']['nome_unidade']
        texto_rodape = self.dados['data_geracao_documento']
        data_geracao = self.string_to_date(self.dados['data_geracao'])

        self.registro.tipo_unidade = tipo_unidade
        self.registro.nome_unidade = nome_unidade
        self.registro.texto_rodape = texto_rodape
        self.registro.data_geracao = data_geracao

        self.registro.save()

