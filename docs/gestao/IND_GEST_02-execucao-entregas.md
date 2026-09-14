# G02 — Execução das Entregas

| Campo | Definição |
| --- | --- |
| Código/namespace | `G02` / `IND_GEST_02` |
| Versão inicial | `1.0.0` |
| Estado | D18 homologada; recertificação automática na GR2 |
| Tempo | histórico PE até o último ciclo fechado + fotografia PT na data de execução |
| Produtos | agregado por entrega, trilha histórica, relatório complementar e anexo nominal restrito |

## Finalidade

Descrever como as entregas dos Planos de Entregas foram executadas e reconciliar o
resultado formal do PE com evidências operacionais dos Planos de Trabalho. O G02 não
produz score sintético, não avalia automaticamente servidores e não usa atividade de
PT como substituta do progresso formal da entrega.

## Perspectivas organizacionais

- **Dona:** uma linha por entrega e ciclo da unidade dona do PE, agregando os PT das
  unidades executoras.
- **Executora:** uma linha por entrega, ciclo e unidade dos servidores com PT,
  inclusive quando a entrega pertence a outra unidade.

Os campos `unidade_dona_sigla` e `unidade_executora_sigla` nunca são fundidos.

## Lentes temporais

Para execução em 13/09/2026, os eventos de
`planos_entregas_entregas_progressos` são aceitos somente até 31/08/2026 e
organizados por `build_periods_pe()`. PT, vínculos e atividades são o estado
observado em 13/09/2026; essa fotografia não é reconstruída nem atribuída aos meses
anteriores.

O universo operacional contém todo usuário com PT não excluído cuja vigência
intersecte 01/07/2025–13/09/2026. Servidor sem entrega vinculada permanece na
cobertura e é classificado como lacuna de cadastro.

## Reconciliação

1. histórico de PE e evidência de PT;
2. histórico de PE sem vínculo de PT;
3. trabalho registrado em PT sem histórico de progresso do PE;
4. PT ou vínculo sem entrega do PE identificável.

## Métricas e produtos

A visão agregada contém ciclo, unidades, entrega sanitizada, meta, progresso e taxa
de atingimento; registros de execução; PT, servidores e vínculos; força de trabalho;
atividades; horas planejadas/despendidas; cobertura e reconciliação. A trilha mantém
os eventos em ordem de `data_progresso` e sanitiza `registro_execucao`.

O anexo nominal existe somente no produto restrito e limita-se a nome, identificador
interno, número/período do PT, entrega, dedicação e situação das atividades. CPF,
e-mail, telefone e endereço não são consultados nem persistidos. O compartilhável
remove identificação, aplica k≥5 e supressão complementar; abaixo de cinco pessoas,
todo o detalhe é suprimido.

## Fontes e qualidade

Todas as fontes e joins aplicam `deleted_at IS NULL`: PE, entregas, progressos, PT,
vínculos, atividades e unidades. `usuarios` é consultada apenas para o anexo nominal
restrito. O oracle independente valida agregação, cobertura e reconciliação.

## Execução

```text
python -m gestao.runner --analise execucao-entregas --data-execucao 2026-09-13 --regional GR2 --produto restrito
python -m lib.validation_runner --familia gestao --alvo G02 --modo integrado --data-execucao 2026-09-13 --regional GR2
```

Os artefatos ficam em `artefatos_local/gestao/AAAA-MM/escopos/<scope-key>/`. A D18
autorizou a baseline separada do G02 na GR2 e o anexo nominal exclusivamente no
produto restrito. Edições finais exigem manifesto integrado com os 14 alvos em
`CERTIFICADO_AUTOMATICAMENTE`.
