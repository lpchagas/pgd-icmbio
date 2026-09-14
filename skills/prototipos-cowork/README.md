# Protótipos Cowork da CGOV — cópias versionadas

As três skills abaixo operam hoje no Cowork da CGOV e produzem os artefatos que
o bloco S21–S24 pretende substituir. Elas **não** eram versionadas: viviam apenas
na sincronização do Cowork, e as correções feitas nelas se perdiam a cada
máquina.

| Skill | O que faz | Saída |
|---|---|---|
| [`cgov-elaborar-entrega`](cgov-elaborar-entrega/SKILL.md) | Estrutura uma nova entrega no formato da Planilha A | Relatório de cadastro |
| [`cgov-registro-execucao`](cgov-registro-execucao/SKILL.md) | Atualiza o status de uma etapa e recalcula o progresso | Log de registro |
| [`cgov-avaliar-entrega`](cgov-avaliar-entrega/SKILL.md) | Aplica a escala e emite parecer ao fim do ciclo | Parecer de avaliação |

## Por que estão aqui

1. **Durabilidade da correção.** A correção de nomenclatura de 14.09.2026
   (quadrimestre, não trimestre — ver abaixo) precisa sobreviver à próxima
   ressincronização do Cowork.
2. **Rastreabilidade.** São a fonte concreta do esquema das Planilhas A e B, que
   o `schema.sql` deste repositório ainda não representa — o conceito de "etapa"
   não tem tabela nem na migração aplicada nem na planejada.
3. **Referência para S21–S24.** As skills especificadas neste repositório
   substituem estes protótipos; comparar as duas exige ter as duas à mão.

Estas cópias são **referência versionada**, não a instalação ativa. Para
atualizar o comportamento no Cowork, ressincronize a partir daqui.

## Correção aplicada em 14.09.2026

As três cópias trazem uma nota de correção ao final. Em resumo: `Q1/Q2/Q3`
designam **quadrimestres** (01/01–30/04, 01/05–31/08, 01/09–31/12), três por ano,
**sem Q4**. As versões originais os chamavam de trimestres e previam um Q4
implícito — resíduo do ciclo trimestral de 2025.

O peso 0,33 por período sempre esteve correto; o rótulo é que não.

A divergência com o calendário publicado pela CGGE (C-01 / RP20 / Q17) **não**
foi resolvida por esta correção e segue aberta — ver
[`../05_plano-skills-execucao-avaliacao_v1.md`](../05_plano-skills-execucao-avaliacao_v1.md),
seção de conflitos.
