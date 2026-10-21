Pontos de impacto para ativar a substituição
O que precisa ser feito para colocar a pipeline no ar (considerar para cada Validação migrada individualmente)
1. DespesaCreateSerializer.validate() e validate_rateios()

Ao ativar o bloco comentado em validate() (já documentado no serializer):

- Remover a chamada ValidacaoDespesaService.validar_rateios_serializer() de validate_rateios() — a função pode virar um simples return value
- Remover o bloco de verificação de recurso em validate() — coberto por RecursoObrigatorioValidator (REG-001)
- Remover a chamada ValidacaoDespesaService.validar_periodo_e_contas() — coberta pelos validators R07–R16
Remover o import de ValidacaoDespesaService se não houver mais usos
2. DespesaService._validar_datas() e _validar_datas_update()

Marcados com # [PIPELINE] no service. Podem ser removidos. O _validar_datas_update() ainda normaliza defaults de update (setdefault), mas o DespesaContextBuilder.build() já faz isso corretamente via get(field) com fallback na instância.

3. DespesaService._processar_pagamento_antecipado()

Após a pipeline, validated_data["motivos_pagamento_antecipado"] e validated_data["outros_motivos_pagamento_antecipado"] já chegam processados pelo apply() do PagamentoAntecipadoValidator. O método pode ser simplificado para apenas pop sem validação ou mutação:


motivos = validated_data.pop("motivos_pagamento_antecipado", [])
outros = validated_data.get("outros_motivos_pagamento_antecipado") or ""
return motivos, outros
4. DespesaService._atualizar_rateios()

Os blocos de validação (R17–R20) e de mutação (R21 — rateio.update({...})) podem ser removidos. A pipeline já validou e mutou ctx.rateios (que é a mesma referência de validated_data["rateios"]). O service fica responsável apenas pela persistência.

5. DespesaService._processar_impostos() e _processar_impostos_update()

O check if not rateios: raise ValidationError(...) (REG-012) pode ser removido — ImpostosValidator garante isso antes do service rodar. Marcados com # [PIPELINE].

Código fora do escopo da pipeline (responsabilidade permanente do service)
Ponto	Motivo
Despesa.objects.create(**validated_data)	Persistência — fora do escopo de validação
despesa.verifica_data_documento_vazio()	Efeito pós-criação no model
cls._cria_atualiza_fornecedor()	Side effect externo (model Fornecedor)
cls._criar_rateios() / RateioDespesa.objects.create/update	Persistência de rateios
cls._aplicar_motivos() / despesa.motivos_pagamento_antecipado.set(...)	Persistência M2M
cls._processar_impostos() — criação/update das despesas de imposto	Persistência com lógica de PC devolvida
cls._finalizar_despesa() — atualiza_status(), set_despesa_anterior_ao_uso_do_sistema(), save()	Finalização pós-persistência
Retry loop por DatabaseError no update() do serializer	Infra de resiliência, não regra de negócio
Sugestões de melhoria
1. Remover double-fetch do RateioDespesa em MudancaAplicacaoValidator
validate() e apply() fazem o mesmo RateioDespesa.objects.filter(uuid=...).first() para cada rateio. Isso dobra as queries. Alternativa: adicionar um campo _cache_rateios: dict ao DespesaDtoContext para reuso entre fases (preenchido no validate(), lido no apply()).

2. ValidacaoDespesaService pode ser deprecado gradualmente
Após a pipeline cobrir todas as regras, ValidacaoDespesaService.validar_rateios_serializer() e validar_periodo_e_contas() ficam órfãos. Marcar como deprecated e remover em seguida.

3. Testes diretos no serializer quebrarão
Tests que stubam ValidacaoDespesaService precisarão ser reescritos para usar os validators diretamente. Criar fixtures de DespesaDtoContext facilita testes unitários dos validators sem passar pelo serializer.

4. Callers que usam DespesaService diretamente (bypassing serializer)
Management commands ou tarefas Celery que chamam o service diretamente não passam pela pipeline — ficam sem as validações. Considerar mover a execução da pipeline para dentro do service com um flag skip_pipeline=False.

5. Atomicidade com SolicitacaoAcerto (Fluxos 3 e 4)
O comentário em create() já documenta isso: o vínculo com SolicitacaoAcertoDocumento deveria acontecer dentro do mesmo @transaction.atomic do service para garantir consistência. Hoje requer um segundo request do frontend.