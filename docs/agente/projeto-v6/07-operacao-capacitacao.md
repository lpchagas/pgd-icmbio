# 07 — Operação e capacitação

## 1. Para usuários não técnicos

O agente ainda é um protótipo em construção. Ao usá-lo:

1. informe o objetivo e o contexto estritamente necessário;
2. escolha a skill sugerida ou confirme a proposta;
3. confira fontes, regras, alertas e dados ausentes;
4. responda apenas às perguntas que puder comprovar;
5. registre a decisão humana quando solicitada;
6. não envie dado pessoal, sensível ou restrito sem autorização;
7. reporte resposta sem fonte, número inesperado ou decisão automática.

Estados: `aguardando_dados` pede informação; `aguardando_decisao` pede autoridade humana;
`erro` não deve ser contornado inventando dado.

## 2. Pré-requisitos técnicos

- Windows;
- Git;
- Python e `.venv` do projeto;
- MySQL84 ativo;
- credenciais locais no `.env`;
- acesso Denodo apenas para tutoriais que o exigem;
- repositório `C:\Projetos\pgd-icmbio` (monorepo; o agente fica em `agente/`).

## 3. T1 — preparar ambiente

**Objetivo:** obter uma cópia funcional sem alterar dados.

```powershell
cd C:\Projetos\pgd-icmbio
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-agente.txt
```

Resultado: ambiente local isolado. Se `.venv` já existir, não o recrie sem necessidade.

## 4. T2 — ciclo seguro de Git

```powershell
git status --short
git pull --ff-only
git switch -c codex/nome-da-alteracao
```

Antes de publicar: revisar status, diff, segredos e `git log origin/main..HEAD --oneline`.
Nunca presumir que somente o último commit será enviado.

## 5. T3 — configuração e segredos

Copie apenas a estrutura de `.env.example` para `.env` e preencha localmente. Variáveis
principais usam prefixos `MYSQL_*` e `DENODO_*`. O `.env` nunca entra no Git.

Resultado esperado: `agente/dados/db.py` consegue abrir conexão sem imprimir senha.

## 6. T4 — validar MySQL e versões

```powershell
.venv\Scripts\python src\dados\versoes.py --teste
```

O teste cria versões dentro de transação e executa rollback. Resultado esperado: histórico
v1→v2 preservado e banco limpo. Se falhar, não contorne triggers com `root`.

## 7. T5 — API e motor de skills

Estes componentes são planejados e ainda não existem. Quando I1 os criar, o runbook será:

```powershell
.venv\Scripts\python -m uvicorn src.api.main:app --reload
```

Abrir `/docs`, executar caso sintético e conferir contrato, fontes e execução. Até o código
existir, este tutorial é uma especificação operacional, não uma promessa de comando válido.

## 8. T6 — Denodo

```powershell
.venv\Scripts\python src\dados\sincronizar_ref.py
```

Pré-requisito: rota e credenciais autorizadas. A sincronização é somente leitura e grava
espelhos mínimos no MySQL. Falha de rota não autoriza usar dados inventados.

## 9. T7 — RAG local

Pipeline futuro:

1. selecionar itens permitidos no índice;
2. extrair/OCR localmente;
3. anexar metadados de fonte, versão, vigência e acesso;
4. indexar em `data/vectorstore/`;
5. executar bateria de perguntas;
6. conferir citações e recusas;
7. excluir/reindexar fonte revogada.

`data/vectorstore/` e binários do corpus permanecem fora do Git.

## 10. T8 — testes

Quando a suíte existir, executar testes unitários, contrato e integração conforme o
README técnico. Testes com banco devem usar base de teste ou rollback. Resultados de QA
vão para `docs/testes/` (pasta planejada) sem dados pessoais.

## 11. T9 — backup e restauração

Backup automático: tarefa `pgd_agente_backup`, diariamente às 19h, retenção de 14 dias.

Backup manual:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File src\dados\backup.ps1
```

Restauração é operação controlada: confirmar arquivo, destino e credencial; preservar o
banco atual; testar preferencialmente em banco separado; validar migrações e contagens.

## 12. T10 — diagnóstico

| Sintoma | Conferir | Não fazer |
| --- | --- | --- |
| MySQL indisponível | serviço `MySQL84` e log | remover/reinstalar sem backup |
| Denodo falha | rede, rota, variáveis e driver | inventar resultado |
| Unicode quebrado | console/UTF-8 | regravar fonte sem conferir encoding |
| Link documental falha | caminho relativo e nome real | apontar para arquivo ignorado público |
| Trigger rejeita UPDATE | serviço de versões | desativar trigger |
| RAG não cita | metadados e recuperação | aceitar texto fluente sem fonte |

## 13. T11 — criar ou revisar skill

1. Copiar `capacidades/especificacoes/TEMPLATE_SKILL.md`.
2. Usar ID não reutilizado.
3. Preencher objetivo, entradas, saídas, regras e limites.
4. Vincular fontes e dependências.
5. Criar exemplos e testes antes do código.
6. Separar cálculo de inferência.
7. Revisar privacidade.
8. Atualizar catálogo e cronograma.

## 14. T12 — segurança antes de publicar

```powershell
git status --short --untracked-files=all
git diff --check
git log origin/main..HEAD --oneline
rg -n "PASS|SENHA|CPF|[0-9]{11}" src docs skills README.md
```

Resultados genéricos exigem revisão manual: placeholders e hashes podem gerar falso
positivo. Informar todos os commits de saída antes de `git push`.

## 15. Escalonamento

| Tema | Escalar para |
| --- | --- |
| regra/vigência | analistas e autoridade competente |
| dado pessoal/LGPD | governança/encarregado conforme rito institucional |
| Denodo/rede | TI/serviço responsável |
| licença/publicação | administração Microsoft/TI |
| perda/corrupção | responsável técnico, usando backup |
| conflito de fonte | Q5 e `regras_conflitos` |

## 16. Reversão documental

Antes de editar, conferir `git status`; alterações não commitadas podem ser comparadas com
`git diff`. Não usar comandos destrutivos para apagar trabalho do usuário. Arquivos
versionados removidos permanecem recuperáveis pelo histórico, mas a recuperação deve ser
intencional e restrita ao alvo.
