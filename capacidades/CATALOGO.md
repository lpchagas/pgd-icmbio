# Catálogo de capacidades

Estado de cada item do portfólio, na escala do plano de reorganização (§7.5):
**disponível → testado → homologado**, antes disso **especificado** ou **planejado**.
Nenhum item é marcado como homologado sem a evidência correspondente.

## Indicadores e relatórios (em produção)

| Item | Estado | Evidência | Pendência |
| --- | --- | --- | --- |
| Indicadores OCDE I01–I12 | homologado nos pilotos CGOV, COCAGE e GR2 | Certificação automática A1–A5 por escopo, com as versões da D35, o I03 3.1.0 (D39), o I04 2.1.0 e o I09 3.0.3 (D41), o I05 3.0.2, o I07 3.2.0 e o I08 3.2.0 (D43); aceites registrados por piloto (evidência no acervo privado) | Expansão nacional (D36) **liberada para os 12** (1ª etapa na D42, 2ª etapa na D44), com baseline nacional homologada; notas ao painel sobre duplicidades atômicas (I01, I05–I08) e força de trabalho fora de 0–100 (I07, I08); I05 só na visão estatística |
| Indicadores de gestão G01 e G02 | homologado nos pilotos CGOV, COCAGE e GR2 | Idem (D17, D18, D35, D38, D40, D42, D44) | G01 liberado no escopo nacional para a COCAGE, no produto restrito (D44, D45); G02: expansão além dos pilotos suspensa (D16) |
| Relatório Gerencial V2 e Relatório de Execução de Entregas | disponível nos pilotos | Consome os A2 certificados de cada piloto | Reemissão dos relatórios GR2 anteriores ao recorte pela hierarquia do PETRVS (D21) |
| Relatório cumulativo anonimizado | disponível nos pilotos | Produtos cumulativos com política de privacidade; fora dos pilotos, barrado pelo gate de liberação | Expansão suspensa (D16) |

## Capacidades do agente S01–S24

Fonte única: [`catalogo.yaml`](catalogo.yaml). A tabela abaixo e as [fichas](fichas/README.md)
são geradas por `tools/gerar_catalogo_capacidades.py`; não as edite à mão (DP-09).
"Especificado" corresponde a "especificada documentalmente; não implementada" na ficha.

<!-- catalogo-capacidades:estado:inicio -->
| ID | Capacidade | Estado | Onda | Gate | Versão da ficha |
| --- | --- | --- | ---: | --- | --- |
| S01 | [Configurador Institucional do PGD](fichas/S01.md) | especificado | 1 | G1 | 0.2 |
| S02 | [Verificador Normativo e de Conformidade](fichas/S02.md) | especificado | 1 | G1 | 0.2 |
| S03 | [Extrator de Competências e Responsabilidades em Entregas](fichas/S03.md) | especificado | 1 | G1 | 0.2 |
| S04 | [Administrador do Catálogo de Entregas](fichas/S04.md) | especificado | 2 | G2 | 0.2 |
| S05 | [Designer de Metas, Indicadores e Critérios de Aceite](fichas/S05.md) | especificado | 1 | G1 | 0.2 |
| S06 | [Auditor de Portfólio de Entregas](fichas/S06.md) | especificado | 2 | G2 | 0.2 |
| S07 | [Planejador de Capacidade da Unidade](fichas/S07.md) | especificado | 2 | G2 | 0.2 |
| S08 | [Matriz de Cobertura das Entregas pela Equipe](fichas/S08.md) | especificado | 2 | G2 | 0.2 |
| S09 | [Designer e Auditor de Encadeamento OKR-D](fichas/S09.md) | especificado | 1 | G1 | 0.2 |
| S10 | [Analisador de Riscos, Dependências e Restrições](fichas/S10.md) | especificado | 2 | G2 | 0.2 |
| S11 | [Assistente de Pactuação do Plano de Entregas](fichas/S11.md) | especificado | 3 | G3 | 0.2 |
| S12 | [Assistente de Pactuação do Plano de Trabalho](fichas/S12.md) | especificado | 3 | G3 | 0.2 |
| S13 | [Check-in de Execução e Monitoramento](fichas/S13.md) | especificado | 3 | G3 | 0.2 |
| S14 | [Gestor de Alterações e Replanejamento](fichas/S14.md) | especificado | 3 | G3 | 0.2 |
| S15 | [Gestor de Contribuições Interunidades](fichas/S15.md) | especificado | 4 | G4 | 0.2 |
| S16 | [Avaliador de Entregas](fichas/S16.md) | especificado | 4 | G4 | 0.2 |
| S17 | [Organizador de Evidências](fichas/S17.md) | especificado | 1 | G1 | 0.2 |
| S18 | [Gerador de Relatório Gerencial do PGD](fichas/S18.md) | especificado | 4 | G4 | 0.2 |
| S19 | [Analisador de Aprendizado entre Ciclos](fichas/S19.md) | especificado | 4 | G4 | 0.2 |
| S20 | [Importador, Exportador e Integrador de Planos](fichas/S20.md) | especificado | 2 | G2 | 0.2 |
| S21 | [Registro de Execução do Plano de Entregas da Unidade](fichas/S21.md) | especificado | 5 | G5 | 0.2 |
| S22 | [Avaliação do Plano de Entregas da Unidade](fichas/S22.md) | especificado | 5 | G5 | 0.2 |
| S23 | [Registro de Execução do Plano de Trabalho do Participante](fichas/S23.md) | especificado | 5 | G5 | 0.2 |
| S24 | [Avaliação do Plano de Trabalho do Participante](fichas/S24.md) | especificado | 5 | G5 | 0.2 |
<!-- catalogo-capacidades:estado:fim -->

## Protótipos fora do monorepo

| Item | Estado | Observação |
| --- | --- | --- |
| [Protótipos Cowork da CGOV](prototipos-cowork/README.md) (`cgov-elaborar-entrega`, `cgov-registro-execucao`, `cgov-avaliar-entrega`) | disponível no Cowork | Cópias versionadas para rastreabilidade; o bloco S21–S24 pretende substituí-los |

Atualize este catálogo na mesma alteração que mudar o estado de uma ficha ou de um indicador.
