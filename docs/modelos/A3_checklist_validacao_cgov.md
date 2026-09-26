# E1 — Checklist de Consulta Humana Excepcional CGOV

**Indicador:** IXX — `<nome do indicador>`
**Período analisado:** `<ex.: T4-2025, Q1-2026, M03-2026>`
**Data da consulta:** DD.MM.AAAA
**Validador(es) CGOV:** `<nome(s)>`

Preencher e salvar como
`artefatos_local/validacao/IND_OCDE_XX.3_PETRVS_consulta_DD.MM.AAAA.pdf`
(ou, para confirmação verbal, ver seção "Confirmação verbal" ao final —
**não deixe a validação sem nenhum artefato físico**: o objetivo deste
checklist é complementar o A3 automatizado quando uma divergência exige
consulta humana, mantendo evidência física em `artefatos_local/validacao/`.)

Instruções gerais: `docs/indicadores/protocolo-validacao.md` §3 (Fase 2).

---

## 1. Unidades amostradas (3–5, perfis variados)

| # | Unidade (sigla) | Perfil (grande/pequena, plano avaliado/ativo) | Valor no PETRVS (sistema ao vivo) | Valor no CSV A2 | Bate? |
|---|---|---|---|---|---|
| 1 | | | | | ☐ Sim ☐ Não |
| 2 | | | | | ☐ Sim ☐ Não |
| 3 | | | | | ☐ Sim ☐ Não |
| 4 (opcional) | | | | | ☐ Sim ☐ Não |
| 5 (opcional) | | | | | ☐ Sim ☐ Não |

## 2. Hipóteses sobre divergências encontradas

Para cada linha "Não" acima, registrar uma hipótese (mesmo que preliminar —
será refinada na Fase 3/A4 pelo analista técnico):

- H1: `<hipótese>`
- H2: `<hipótese>`

## 3. Veredito

☐ **Confirma** — valores do CSV A2 batem com o PETRVS nas unidades amostradas, sem ressalvas
☐ **Confirma com ressalvas** — bate na maioria, mas há hipóteses a investigar (preencher seção 2)
☐ **Diverge** — descolamento relevante entre A2 e PETRVS; aguardar diagnóstico A4/A5 antes de publicar

## 4. Confirmação verbal (usar somente quando não houver PDF de consulta)

Se a validação ocorreu em reunião/conversa informal em vez de consulta
documentada no PETRVS, preencher aqui em vez da seção 1 — isso formaliza
uma confirmação apenas verbal, em vez de deixá-la sem
nenhum registro:

- Data: DD.MM.AAAA
- Quem confirmou (nome, cargo): `<nome>`
- Meio (reunião presencial, chamada, e-mail, chat): `<meio>`
- Resumo do que foi confirmado: `<texto livre>`

---

**Próximo passo:** entregar este checklist preenchido ao analista técnico
para a Fase 3 (`/p4-gerar-a4`) — diagnóstico técnico e elaboração do
relatório A5 (`IND_OCDE_XX.5_relatorio_validacao_DD.MM.AAAA.md` em
`artefatos_local/validacao/`). **Um indicador só deve ser marcado ✅ em
o registro institucional de homologação depois que o A5 correspondente existir nessa
pasta** — ver `tests/regression/test_claude_md_consistency.py`.
