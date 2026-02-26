import csv
import logging
from datetime import datetime
from django.core.files import File
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.devolucao_ao_tesouro import DevolucaoAoTesouro
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from sme_ptrf_apps.utils.anonimizar_cpf_cnpj import anonimizar_cpf

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
    (
        'Recurso',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__periodo__recurso__nome'
    ),
    (
        'Código EOL',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__associacao__unidade__codigo_eol',
    ),
    (
        'Nome Unidade',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__associacao__unidade__nome',
    ),
    (
        'Nome Associação',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__associacao__nome',
    ),
    (
        'DRE',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__associacao__unidade__dre__nome',
    ),
    (
        'Referência do Período da PC',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__periodo__referencia',
    ),
    (
        'Status da PC',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__'
        'prestacao_conta__status',
    ),
    (
        'ID da despesa',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__id',
    ),
    (
        'Número do documento',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__numero_documento',
    ),
    (
        'Tipo do documento',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__tipo_documento__nome',
    ),
    (
        'Data do documento',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_documento',
    ),
    (
        'CPF_CNPJ do fornecedor',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__cpf_cnpj_fornecedor',
    ),
    (
        'Nome do fornecedor',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__nome_fornecedor',
    ),
    (
        'Tipo de transação',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__tipo_transacao__nome',
    ),
    (
        'Número do documento da transação',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__documento_transacao',
    ),
    (
        'Data da transação',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_transacao',
    ),
    (
        'Valor (Despeza)',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_original',
    ),
    (
        'Valor realizado (Despesa)',
        'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_total',
    ),
    ('Tipo de aplicação do recurso', 'aplicacao_recurso'),
    ('Nome do Tipo de Custeio', 'tipo_custeio'),
    ('Descrição da especificação de Material ou Serviço', 'desc_material_serv'),
    ('Nome do tipo de Conta', 'nome_tipo_conta'),
    ('Nome da Ação', 'nome_acao'),
    ('Valor (Rateios)', 'valor_rateio'),
    ('Valor realizado (Rateio)', 'valor_realizado'),
    ('Tipo de devolução', 'tipo_id'),
    ('Descrição do Tipo de devolução', 'tipo_nome'),
    ('Motivo', 'motivo'),
    ('É devolução total?', 'devolucao_total'),
    ('Valor (Devolução)', 'valor'),
    ('Data de devolução ao tesouro', 'data'),
    ('Justificativa (não realização)', 'justificativa'),
]


class ExportacoesDevolucaoTesouroPrestacoesContaService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.dre_codigo_eol = kwargs.get('dre_codigo_eol', None)
        self.cabecalho = CABECALHO
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None
        self.texto_filtro_aplicado = self.get_texto_filtro_aplicado()

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def get_texto_filtro_aplicado(self):
        if self.data_inicio and self.data_final:
            data_inicio_formatada = datetime.strptime(
                str(self.data_inicio), '%Y-%m-%d'
            )
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")

            data_final_formatada = datetime.strptime(
                str(self.data_final), '%Y-%m-%d'
            )
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")

            return f"Filtro aplicado: {data_inicio_formatada} a {data_final_formatada} (data de criação do registro)"

        if self.data_inicio:
            data_inicio_formatada = datetime.strptime(
                str(self.data_inicio), '%Y-%m-%d'
            )
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: A partir de {data_inicio_formatada} (data de criação do registro)"

        if self.data_final:
            data_final_formatada = datetime.strptime(
                str(self.data_final), '%Y-%m-%d'
            )
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: Até {data_final_formatada} (data de criação do registro)"

        return ""

    def exporta_devolucao_tesouro_pc(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_devolucao_tesouro_pc_csv()

    def exporta_devolucao_tesouro_pc_csv(self):
        dados = self.monta_dados()

        with NamedTemporaryFile(
            mode="r+",
            newline='',
            encoding='utf-8',
            prefix=self.nome_arquivo,
            suffix='.csv'
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            write.writerow([cabecalho[0] for cabecalho in self.cabecalho])

            for linha in dados:
                write.writerow(linha) if linha else None

            self.cria_rodape(write)
            self.envia_arquivo_central_download(tmp)

    def monta_dados(self):
        linhas_vertical = []
        despesa_primeira_linha = set()

        for instance in self.queryset:
            linha_horizontal = []

            despesa_id = instance.solicitacao_acerto_lancamento.analise_lancamento.despesa.id
            primeira_linha_da_despesa = despesa_id not in despesa_primeira_linha
            devolucao_ao_tesouro = DevolucaoAoTesouro.objects.filter(despesa_id=despesa_id).first()

            rateios = list(instance.solicitacao_acerto_lancamento.analise_lancamento.despesa.rateios.all())

            for _, campo in self.cabecalho:
                if campo == (
                    "solicitacao_acerto_lancamento__"
                    "analise_lancamento__analise_prestacao_conta__"
                    "prestacao_conta__periodo__recurso__nome"
                ):
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == (
                    "solicitacao_acerto_lancamento__analise_lancamento__"
                    "analise_prestacao_conta__prestacao_conta__associacao__"
                    "unidade__nome"
                ):
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == (
                    "solicitacao_acerto_lancamento__analise_lancamento__"
                    "analise_prestacao_conta__prestacao_conta__associacao__nome"
                ):
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == (
                    "solicitacao_acerto_lancamento__analise_lancamento__"
                    "analise_prestacao_conta__prestacao_conta__associacao__"
                    "unidade__dre__nome"
                ):
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "solicitacao_acerto_lancamento__analise_lancamento__despesa__cpf_cnpj_fornecedor":
                    campo = get_recursive_attr(instance, campo)
                    valor_anonimizado = anonimizar_cpf(campo) if campo else ""
                    linha_horizontal.append(valor_anonimizado)
                    continue

                if campo == "solicitacao_acerto_lancamento__analise_lancamento__despesa__nome_fornecedor":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "solicitacao_acerto_lancamento__analise_lancamento__despesa__documento_transacao":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo in {
                    'aplicacao_recurso',
                    'tipo_custeio',
                    'desc_material_serv',
                    'nome_tipo_conta',
                    'nome_acao',
                    'valor_rateio',
                    'valor_realizado',
                }:
                    linha_horizontal.append('')
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_documento':
                    campo = get_recursive_attr(instance, campo)
                    data_doc_formatado = campo.strftime("%d/%m/%Y") if campo is not None else ''
                    linha_horizontal.append(data_doc_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_transacao':
                    campo = get_recursive_attr(instance, campo)
                    data_tran_formatado = campo.strftime("%d/%m/%Y") if campo is not None else ''
                    linha_horizontal.append(data_tran_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_original':
                    campo = get_recursive_attr(instance, campo)
                    valor_original_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_original_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_total':
                    campo = get_recursive_attr(instance, campo)
                    valor_total_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_total_formatado)
                elif campo == 'tipo_id':
                    linha_horizontal.append(devolucao_ao_tesouro.tipo.id if devolucao_ao_tesouro is not None else '')
                elif campo == 'tipo_nome':
                    tipo_nome = ''
                    if devolucao_ao_tesouro is not None:
                        tipo_nome = devolucao_ao_tesouro.tipo.nome.replace(";", ",")
                    linha_horizontal.append(tipo_nome)
                elif campo == 'motivo':
                    motivo = ''
                    if devolucao_ao_tesouro is not None:
                        motivo = devolucao_ao_tesouro.motivo.replace(";", ",")
                    linha_horizontal.append(motivo)
                elif campo == 'devolucao_total':
                    if devolucao_ao_tesouro is not None:
                        linha_horizontal.append('Sim' if devolucao_ao_tesouro.devolucao_total else 'Não')
                    else:
                        linha_horizontal.append('')
                elif campo == 'valor':
                    valor = ''
                    if devolucao_ao_tesouro is not None:
                        valor = str(devolucao_ao_tesouro.valor).replace(".", ",")
                    linha_horizontal.append(valor)
                elif campo == 'data':
                    data_formatada = ''
                    if devolucao_ao_tesouro is not None and devolucao_ao_tesouro.data:
                        data_formatada = devolucao_ao_tesouro.data.strftime(
                            "%d/%m/%Y"
                        )
                    linha_horizontal.append(data_formatada)
                elif campo == 'justificativa':
                    justificativa = ''
                    if instance.solicitacao_acerto_lancamento.justificativa:
                        justificativa = (
                            instance.solicitacao_acerto_lancamento.justificativa
                            .replace(";", ",")
                        )
                    linha_horizontal.append(justificativa)
                else:
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo)

            if rateios:
                for idx, rateio in enumerate(rateios):
                    linha_nova = linha_horizontal.copy()

                    if primeira_linha_da_despesa and idx == 0:
                        despesa_primeira_linha.add(despesa_id)
                    else:
                        linha_nova[28] = ''

                    linha_nova[17] = rateio.aplicacao_recurso or ''
                    linha_nova[18] = (
                        rateio.tipo_custeio.nome.replace(";", ",")
                        if rateio.tipo_custeio
                        else ''
                    )
                    linha_nova[19] = (
                        rateio.especificacao_material_servico.descricao.replace(
                            ";", ","
                        )
                        if rateio.especificacao_material_servico
                        else ''
                    )
                    linha_nova[20] = (
                        rateio.conta_associacao.tipo_conta.nome.replace(";", ",")
                        if rateio.conta_associacao
                        else ''
                    )
                    linha_nova[21] = (
                        rateio.acao_associacao.acao.nome.replace(";", ",")
                        if rateio.acao_associacao
                        else ''
                    )
                    linha_nova[22] = (
                        str(rateio.valor_rateio).replace(".", ",")
                        if rateio.valor_rateio
                        else ''
                    )
                    linha_nova[23] = (
                        str(rateio.valor_original).replace(".", ",")
                        if rateio.valor_original
                        else ''
                    )

                    linhas_vertical.append(linha_nova)
            else:
                logger.info(
                    "Escrevendo linha %s de status de prestação de conta de "
                    "custeio %s.",
                    linha_horizontal,
                    instance.id,
                )
                despesa_primeira_linha.add(despesa_id)
                linhas_vertical.append(linha_horizontal)

        return linhas_vertical

    def filtra_range_data(self, field):
        if self.data_inicio and self.data_final:
            self.data_inicio = datetime.strptime(
                f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S'
            )
            self.data_final = datetime.strptime(
                f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S'
            )

            self.queryset = self.queryset.filter(
                **{f'{field}__range': [self.data_inicio, self.data_final]}
            )
        elif self.data_inicio and not self.data_final:
            self.data_inicio = datetime.strptime(
                f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S'
            )

            self.queryset = self.queryset.filter(
                **{f'{field}__gt': self.data_inicio}
            )

        elif self.data_final and not self.data_inicio:
            self.data_final = datetime.strptime(
                f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S'
            )

            self.queryset = self.queryset.filter(
                **{f'{field}__lt': self.data_final}
            )
        return self.queryset

    def cria_registro_central_download(self):
        logger.info("Criando registro na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            self.texto_filtro_aplicado,
            self.dre_codigo_eol
        )
        self.objeto_arquivo_download = obj

    def envia_arquivo_central_download(self, tmp):
        try:
            logger.info("Salvando arquivo download...")
            self.objeto_arquivo_download.arquivo.save(
                name=self.objeto_arquivo_download.identificador,
                content=File(tmp)
            )
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            self.objeto_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")
        except Exception as e:
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            self.objeto_arquivo_download.msg_erro = str(e)
            self.objeto_arquivo_download.save()
            logger.error("Erro arquivo download...")

    def texto_rodape(self):
        # Usa o horário de início do processamento (criado_em do registro na central de download)
        inicio = None
        if self.objeto_arquivo_download and getattr(self.objeto_arquivo_download, 'criado_em', None):
            inicio = self.objeto_arquivo_download.criado_em
        else:
            inicio = datetime.now()

        data_hora_inicio = inicio.strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo solicitado via {self.ambiente} pelo usuário {self.user} em {data_hora_inicio}"

        return texto

    def cria_rodape(self, write):
        rodape = []

        rodape.append(" ")
        write.writerow(rodape)
        rodape.clear()

        texto = self.texto_rodape()

        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()

        data_hora_disponibilizado = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape.append(f"Arquivo disponibilizado em {data_hora_disponibilizado}")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()
