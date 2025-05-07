import waffle

from waffle.decorators import waffle_flag

from django.conf import settings
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter, SimpleRouter

from sme_ptrf_apps import __version__
from sme_ptrf_apps.core.api.views import (
    AssociacoesViewSet,
    ParametrizacoesAssociacoesViewSet,
    AtasViewSet,
    DemonstrativoFinanceiroViewSet,
    MembroAssociacaoViewSet,
    PeriodosViewSet,
    PrestacoesContasViewSet,
    RelacaoBensViewSet,
    ProcessosAssociacaoViewSet,
    UnidadesViewSet,
    ConciliacoesViewSet,
    ContasAssociacoesViewSet,
    NotificacaoViewSet,
    DresViewSet,
    TiposDevolucaoAoTesouroViewSet,
    MotivosDevolucaoAoTesouroViewSet,
    TiposContaViewSet,
    ComentariosAnalisesPrestacoesViewSet,
    AcaoAssociacaoViewSet,
    ParametrizacoesAcoesAssociacaoViewSet,
    AcoesViewSet,
    ArquivoViewSet,
    TagsViewSet,
    ModelosCargasViewSet,
    AmbientesViewSet,
    ArquivosDownloadViewSet,
    TiposAcertoLancamentoViewSet,
    TiposAcertoDocumentoViewSet,
    AnalisesPrestacoesContasViewSet,
    PresentesAtaViewSet,
    AnaliseContaPrestacaoContaViewSet,
    ParametrosUeViewSet,
    AnaliseLancamentoPrestacaoContaViewSet,
    AnaliseDocumentoPrestacaoContaViewSet,
    FalhaGeracaoPcViewSet,
    SolicitacaoEncerramentoContaAssociacaoViewset,
    MotivoRejeicaoEncerramentoContaAssociacaoViewset,
    feature_flags,
    AcoesPddeViewSet,
    CategoriaPddeViewSet,
    ReceitaPrevistaPaaViewSet,
    FonteRecursoPaaViewSet,
    RecursoProprioPaaViewSet
)
from sme_ptrf_apps.core.api.views.prestacoes_contas_reprovadas_nao_apresentacao_viewset import \
    PrestacaoContaReprovadaNaoApresentacaoViewSet
from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet
from sme_ptrf_apps.despesas.api.views.tipo_documento_viewset import TiposDocumentoViewSet
from sme_ptrf_apps.despesas.api.views.especificacoes_viewset import EspecificacaoMaterialServicoViewSet, \
    ParametrizacaoEspecificacoesMaterialServicoViewSet
from sme_ptrf_apps.despesas.api.views.fornecedores_viewset import FornecedoresViewSet
from sme_ptrf_apps.despesas.api.views.rateios_despesas_viewset import RateiosDespesasViewSet
from sme_ptrf_apps.despesas.api.views.tipos_custeio_viewset import TiposCusteioViewSet
from sme_ptrf_apps.despesas.api.views.tipos_transacao_viewset import TiposTransacaoViewSet
from sme_ptrf_apps.despesas.api.views.motivos_pagamento_antecipado_viewset import MotivosPagamentoAntecipadoViewSet
from sme_ptrf_apps.dre.api.views import (
    FaqCategoriasViewSet,
    FaqsViewSet,
    TecnicosDreViewSet,
    AtribuicaoViewset,
    RelatoriosConsolidadosDREViewSet,
    JustificativasRelatoriosConsolidadosDreViewSet,
    MotivoAprovacaoRessalvaViewSet,
    MotivoAprovacaoRessalvaParametrizacaoViewSet,
    MotivoReprovacaoViewSet,
    ComissoesViewSet,
    MembrosComissoesViewSet,
    AnosAnaliseRegularidadeViewSet,
    AtaParecerTecnicoViewset,
    ConsolidadosDreViewSet,
    ParametrosDreViewSet,
    ValoresReprogramadosViewSet,
    LaudaViewSet,
    ComentariosAnalisesConsolidadosDREViewSet,
    AnalisesDocumentosConsolidadoDreViewSet,
    AnalisesConsolidadoDreViewSet,
)
from sme_ptrf_apps.sme.api.views import (
    SaldosBancariosSMEViewSet,
    SaldosBancariosSmeDetalhesAsocciacoesViewSet,
    ParametrosSmeViewSet,
    ExportacoesDadosViewSet
)
from sme_ptrf_apps.receitas.api.views import (
    ReceitaViewSet,
    RepasseViewSet,
    MotivosEstornoViewSet,
    TipoReceitaViewSet
)
from sme_ptrf_apps.paa.api.views import (
    PeriodoPaaViewSet,
    ParametrosPaaViewSet,
    PaaViewSet
)
from sme_ptrf_apps.users.api.views import (
    EsqueciMinhaSenhaViewSet,
    LoginView,
    RedefinirSenhaViewSet,
    UserViewSet, # TODO - Remover ao fim da implantação da nova gestão de usuários
    UsuariosViewSet,
    GruposViewSet
)

from sme_ptrf_apps.mandatos.api.views import MandatosViewSet, ComposicoesViewSet, OcupantesCargosViewSet, CargosComposicoesViewSet

from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs_view import (
    SimuladorDeLogsView,
    SimuladorDeLogsAsyncView,
    SimuladorDeLogsSecudarioView,
    SimuladorDeLogsSecundarioAsyncView,
)

@api_view()
def versao(request):
    versao = __version__
    if waffle.flag_is_active(request, 'teste-flag'):
        versao = "teste-flag"
    return Response({"versao": versao})


@api_view()
@waffle_flag('teste-flag')
def teste_flag_view(request):
    return Response({"mensagem": "Se está vendo essa mensagem é porque a teste-flag está ativa."})


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("usuarios", UserViewSet, basename="usuarios") # TODO - Remover ao fim da implantação da nova gestão de usuários
router.register("usuarios-v2", UsuariosViewSet, basename="usuarios-v2")
router.register("grupos", GruposViewSet, basename="grupos")
router.register("despesas", DespesasViewSet, basename="despesas")
router.register("especificacoes", EspecificacaoMaterialServicoViewSet, basename="especificacoes")
router.register("especificacoes-materiais-servicos", ParametrizacaoEspecificacoesMaterialServicoViewSet, basename="especificacoes-materiais-servicos")
router.register("rateios-despesas", RateiosDespesasViewSet, basename="rateios-despesas")
router.register("receitas", ReceitaViewSet, basename="receitas")
router.register("tipos-receitas", TipoReceitaViewSet, basename="tipos-receitas")
router.register("fornecedores", FornecedoresViewSet, basename="fornecedores")
router.register("associacoes", AssociacoesViewSet, basename="associacoes")
router.register("parametrizacoes-associacoes", ParametrizacoesAssociacoesViewSet, basename="parametrizacoes-associacoes")
router.register("repasses", RepasseViewSet, basename='repasses-pendentes')
router.register("periodos", PeriodosViewSet, basename="periodos")
router.register("prestacoes-contas", PrestacoesContasViewSet, basename="prestacoes-contas")
router.register("demonstrativo-financeiro", DemonstrativoFinanceiroViewSet, basename="demonstrativo-financeiro")
router.register("relacao-bens", RelacaoBensViewSet, basename="relacao-bens")
router.register("atas-associacao", AtasViewSet, basename="atas-associacao")
router.register("membros-associacao", MembroAssociacaoViewSet, basename="membros-associacao")
router.register("esqueci-minha-senha", EsqueciMinhaSenhaViewSet, basename="esqueci-minha-senha")
router.register("redefinir-senha", RedefinirSenhaViewSet, basename="redefinir-senha")
router.register("processos-associacao", ProcessosAssociacaoViewSet, basename="processos-associacao")
router.register("unidades", UnidadesViewSet, basename="unidades")
router.register("tecnicos-dre", TecnicosDreViewSet, basename="tecnicos-dre")
router.register("faq-categorias", FaqCategoriasViewSet, basename="faq-categorias")
router.register("faqs", FaqsViewSet, basename="faqs")
router.register("atribuicoes", AtribuicaoViewset, basename="atribuicoes")
router.register("conciliacoes", ConciliacoesViewSet, basename='conciliacoes')
router.register("notificacoes", NotificacaoViewSet, basename='notificacoes')
router.register("dres", DresViewSet, basename='dres')
router.register("tipos-devolucao-ao-tesouro", TiposDevolucaoAoTesouroViewSet, basename='tipos-devolucao-ao-tesouro')
router.register("motivos-devolucao-ao-tesouro", MotivosDevolucaoAoTesouroViewSet, basename='motivos-devolucao-ao-tesouro')
router.register("tipos-conta", TiposContaViewSet, basename='tipos-conta')
router.register("tipos-documento", TiposDocumentoViewSet, basename='tipos-documento')
router.register("comentarios-de-analises", ComentariosAnalisesPrestacoesViewSet, basename='comentarios-de-analises')
router.register("relatorios-consolidados-dre", RelatoriosConsolidadosDREViewSet, basename="relatorios-consolidados-dre")
router.register("justificativas-relatorios-consolidados-dre", JustificativasRelatoriosConsolidadosDreViewSet, basename="justificativas-relatorios-consolidados-dre")
router.register("motivos-aprovacao-ressalva", MotivoAprovacaoRessalvaViewSet, basename="motivos-aprovacao-ressalva")
router.register("motivos-aprovacao-ressalva-parametrizacao", MotivoAprovacaoRessalvaParametrizacaoViewSet, basename="motivos-aprovacao-ressalva-parametrizacao")
router.register("motivos-reprovacao", MotivoReprovacaoViewSet, basename="motivos-reprovacao")
router.register("acoes-associacoes", AcaoAssociacaoViewSet, basename="acoes-associacoes")
router.register("contas-associacoes", ContasAssociacoesViewSet, basename="contas-associacoes")
router.register("parametrizacoes-acoes-associacoes", ParametrizacoesAcoesAssociacaoViewSet, basename="parametrizacoes-acoes-associacoes")
router.register("acoes", AcoesViewSet, basename="acoes")
router.register("arquivos", ArquivoViewSet, basename="arquivos")
router.register("tags", TagsViewSet, basename="tags")
router.register("modelos-cargas", ModelosCargasViewSet, basename="modelos-cargas")
router.register("tipos-custeio", TiposCusteioViewSet, basename="tipos-custeio")
router.register("tipos-transacao", TiposTransacaoViewSet, basename="tipos-transacao")
router.register("ambientes", AmbientesViewSet, basename="ambientes")
router.register("saldos-bancarios-sme", SaldosBancariosSMEViewSet, basename="saldos-bancarios-sme")
router.register("saldos-bancarios-sme-detalhes", SaldosBancariosSmeDetalhesAsocciacoesViewSet, basename="saldos-bancarios-sme-detalhes")
router.register("arquivos-download", ArquivosDownloadViewSet, basename="arquivos-download")
router.register("tipos-acerto-lancamento", TiposAcertoLancamentoViewSet, basename="tipos-acerto-lancamento")
router.register("tipos-acerto-documento", TiposAcertoDocumentoViewSet, basename="tipos-acerto-documento")
router.register("analises-prestacoes-contas", AnalisesPrestacoesContasViewSet, basename="analises-prestacoes-contas")
router.register("presentes-ata", PresentesAtaViewSet, basename="presentes-ata")
router.register("analises-conta-prestacao-conta", AnaliseContaPrestacaoContaViewSet, basename="analises-conta-prestacao-conta")
router.register("analises-lancamento-prestacao-conta", AnaliseLancamentoPrestacaoContaViewSet, basename="analises-lancamento-prestacao-conta")
router.register("analises-documento-prestacao-conta", AnaliseDocumentoPrestacaoContaViewSet, basename="analises-documento-prestacao-conta")
router.register("comissoes", ComissoesViewSet, basename="comissoes")
router.register("membros-comissoes", MembrosComissoesViewSet, basename="membros-comissoes")
router.register("anos-analise-regularidade", AnosAnaliseRegularidadeViewSet, basename="anos-analise-regularidade")
router.register("ata-parecer-tecnico", AtaParecerTecnicoViewset, basename="ata-parecer-tecnico")
router.register("motivos-pagamento-antecipado", MotivosPagamentoAntecipadoViewSet, basename="motivos-pagamento-antecipado")
router.register("motivos-estorno", MotivosEstornoViewSet, basename="motivos-estorno")
router.register("consolidados-dre", ConsolidadosDreViewSet, basename="consolidados-dre")
router.register("parametros-ue", ParametrosUeViewSet, basename="parametros-ue")
router.register("parametros-dre", ParametrosDreViewSet, basename="parametros-dre")
router.register("parametros-sme", ParametrosSmeViewSet, basename="parametros-sme")
router.register("valores-reprogramados", ValoresReprogramadosViewSet, basename="valores-reprogramados")
router.register("exportacoes-dados", ExportacoesDadosViewSet, basename="exportacoes-dados")
router.register("laudas", LaudaViewSet, basename="laudas")
router.register("comentarios-de-analises-consolidados-dre", ComentariosAnalisesConsolidadosDREViewSet, basename="comentarios-de-analises-consolidados-dre")
router.register("analises-documentos-consolidados-dre", AnalisesDocumentosConsolidadoDreViewSet, basename="analises-documentos-consolidados-dre")
router.register("analises-consolidados-dre", AnalisesConsolidadoDreViewSet, basename="analises-consolidados-dre")
router.register("falhas-geracao-pc", FalhaGeracaoPcViewSet, basename="falhas-geracao-pc")
router.register("solicitacoes-encerramento-conta", SolicitacaoEncerramentoContaAssociacaoViewset, basename="solicitacoes-encerramento-conta")
router.register("motivos-rejeicao-encerramento-conta", MotivoRejeicaoEncerramentoContaAssociacaoViewset, basename="motivos-rejeicao-encerramento-conta")
router.register("categorias-pdde", CategoriaPddeViewSet, basename="categorias-pdde")
router.register("acoes-pdde", AcoesPddeViewSet, basename="acoes-pdde")
router.register("receitas-previstas-paa", ReceitaPrevistaPaaViewSet, basename="receitas-previstas-paa")
router.register("mandatos", MandatosViewSet, basename="mandatos")
router.register("composicoes", ComposicoesViewSet, basename="composicoes")
router.register("ocupantes-cargos", OcupantesCargosViewSet, basename="ocupantes-cargos")
router.register("cargos-composicao", CargosComposicoesViewSet, basename="cargos-composicao")
router.register("prestacoes-contas-reprovadas-nao-apresentacao", PrestacaoContaReprovadaNaoApresentacaoViewSet, basename="prestacoes-contas-reprovadas-nao-apresentacao")
router.register("paa", PaaViewSet, basename='paa')
router.register("fontes-recursos-paa", FonteRecursoPaaViewSet, basename='fonte_recurso_paa')
router.register("recursos-proprios-paa", RecursoProprioPaaViewSet, basename='recursos_proprios_paa')
router.register("periodos-paa", PeriodoPaaViewSet, basename='periodos_paa')
router.register("parametros-paa", ParametrosPaaViewSet, basename='parametros_paa')


app_name = "api"
urlpatterns = router.urls
urlpatterns += [
    path("versao", versao),
    path("teste-flag", teste_flag_view),
    path("login", LoginView.as_view()),
    path("feature-flags", feature_flags),
    path("simular-logs", SimuladorDeLogsView.as_view()),
    path("simular-logs-sec", SimuladorDeLogsSecudarioView.as_view()),
    path("simular-logs-async", SimuladorDeLogsAsyncView.as_view()),
    path("simular-logs-sec-async", SimuladorDeLogsSecundarioAsyncView.as_view()),
]
