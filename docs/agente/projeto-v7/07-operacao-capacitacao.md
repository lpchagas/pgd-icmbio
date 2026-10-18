# 07 — Operação e capacitação

## 1. Para usuários não técnicos

O agente ainda é um protótipo em construção. Ao usá-lo:

1. informe o objetivo e o contexto estritamente necessário;
2. escolha a skill sugerida ou confirme a proposta;
3. confira fontes, regras, alertas e dados ausentes;
4. responda apenas às perguntas que puder comprovar;
5. registre a decisão humana quando solicitada;
6. não cole dado pessoal, sensível ou restrito em ferramenta externa: o servidor recusa
   esse conteúdo, mas o que você digita no cliente sai do computador;
7. reporte resposta sem fonte, número inesperado, recusa estranha ou decisão automática.

Estados: `aguardando_dados` pede informação; `aguardando_decisao` pede autoridade humana;
`erro` não deve ser contornado inventando dado. Uma recusa por classe de dado significa
que o conteúdo não pode ir para aquele cliente; use o modelo local ou peça o agregado
compartilhável.

## 2. Pré-requisitos técnicos

- Linux/WSL como ambiente principal, com o repositório no filesystem Linux
  (`~/projetos/pgd-icmbio`); no WSL, o systemd ativo;
- Git;
- Python 3.14 e `.venv` do projeto (o CI usa 3.12);
- MySQL 8.4 do pacote `mysql-server` da distribuição, na porta 3306;
- credenciais locais: `.env` (Denodo; nomes em `.env.example`) e `.cnf` (MySQL), fora do Git;
- JDK Linux e driver JDBC da Denodo apenas para tutoriais que acessam o Denodo;
- Claude Code (principal) ou Antigravity (secundário) para desenvolver.

O Windows continua suportado com os equivalentes `.ps1` e `.venv\Scripts\python.exe`
([banco local do agente](../../ambiente/banco-local-agente.md)).

## 3. T1 — preparar ambiente

**Objetivo:** obter uma cópia funcional sem alterar dados.

```bash
cd ~/projetos/pgd-icmbio
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-agente.txt -r requirements-dev.txt
```

Resultado: ambiente local isolado. Se a `.venv` já existir, não a recrie sem necessidade.
As pastas privadas (`artefatos_local/`, `.agents/`, `.claude/` e outras) são links locais
para a pasta sincronizada da equipe e precisam ser recriadas em cada computador
([organização público/privado](../../ambiente/organizacao-publico-privado.md)).

## 4. T2 — ciclo seguro de Git

```bash
git status --short
git pull --ff-only
```

O trabalho é feito direto no `main`, fora de reorganizações. Commit só com autorização e
depois da suíte completa verde. Antes de publicar: revisar status, diff, segredos e
`git log origin/main..HEAD --oneline`. Nunca presumir que só o último commit será enviado.

## 5. T3 — configuração e segredos

Copie apenas a estrutura de `.env.example` para `.env` e preencha localmente. As
variáveis do Denodo usam o prefixo `DENODO_*`; as credenciais do MySQL ficam em arquivos
`.cnf` locais, fora do Git. Nenhum dos dois entra no Git, e nenhum valor é exibido em log
ou documento.

Resultado esperado: `agente/dados/db.py` abre a conexão sem imprimir senha.

## 6. T4 — validar MySQL e versões

```bash
systemctl is-active mysql
.venv/bin/python agente/dados/versoes.py --teste
```

O teste cria versões dentro de transação e executa rollback. Resultado esperado: histórico
v1→v2 preservado e banco limpo. Se falhar, não contorne triggers com `root`.

## 7. T5 — servidor MCP e motor de skills

Estes componentes são planejados (C01–C03) e ainda não existem. Quando existirem, o
runbook mostrará como:

1. iniciar o servidor MCP local (`agente/mcp/`);
2. registrá-lo no Claude Code e no modelo local;
3. executar um caso sintético e conferir contrato, classe do dado, fontes e execução;
4. confirmar a recusa de um pedido de conteúdo institucional pelo cliente externo.

Até o código existir, este tutorial é uma especificação operacional, não uma promessa de
comando válido. O adaptador FastAPI, se criado, terá runbook próprio.

## 8. T6 — Denodo

```bash
.venv/bin/python agente/dados/sincronizar_ref.py
```

Pré-requisitos: IP liberado pelo Dataprev, credenciais no `.env`, JDK Linux e
`DENODO_JVM_DLL` apontando para a `libjvm.so`
([acesso ao Denodo](../../ambiente/acesso-denodo-dbeaver.md)). A sincronização é somente
leitura e grava espelhos mínimos no MySQL. Falha de rota não autoriza usar dados
inventados.

## 9. T7 — indicadores para o agente

O agente não extrai indicador: lê os A2 certificados do ciclo gerencial mensal dos
pilotos. Para atualizá-los, rode o comando padrão dos pilotos com a data de execução do
ciclo, por exemplo:

```bash
.venv/bin/python -m tools.executar_pilotos --capacidade ocde --data-execucao AAAA-MM-DD --modo real --validar
```

Os resultados saem separados por piloto; nunca some taxas entre pilotos.

## 10. T8 — RAG local

Pipeline futuro (C04 e Onda 1):

1. selecionar itens permitidos no índice;
2. extrair/OCR localmente;
3. anexar metadados de fonte, versão, vigência, acesso e classe;
4. indexar em `data/vectorstore/`;
5. executar bateria de perguntas;
6. conferir citações e recusas;
7. excluir/reindexar fonte revogada.

`data/vectorstore/` e binários do corpus permanecem fora do Git.

## 11. T9 — testes

Suíte completa, offline (não abre Denodo nem MySQL):

```bash
.venv/bin/python -m pytest tests -q -p no:cacheprovider
```

Testes contra MySQL, só na instância isolada:

```bash
agente/dados/mysql_isolada.sh iniciar
PGD_MYSQL_TESTE=1 .venv/bin/python -m pytest -m mysql tests/agente
```

Resultados de QA das skills vão para `docs/testes/` (pasta planejada), sem dados pessoais.

## 12. T10 — backup e restauração

Backup automático: timer de usuário do systemd `pgd-agente-backup`, diariamente às 19h,
retenção de 14 dias. No WSL, o timer só dispara com a distribuição em execução; o backup
perdido roda na próxima inicialização.

```bash
systemctl --user list-timers pgd-agente-backup.timer
agente/dados/backup.sh --somente-validar
```

Restauração é operação controlada, sempre na instância isolada (porta 3307):

```bash
.venv/bin/python agente/dados/banco_teste.py restaurar --dump <arquivo .dump.sql>
```

O script recusa a instância principal e relata só a estrutura (tabelas, triggers, versão
do schema). Detalhes: [banco local do agente](../../ambiente/banco-local-agente.md).

## 13. T11 — diagnóstico

| Sintoma | Conferir | Não fazer |
| --- | --- | --- |
| MySQL indisponível | `systemctl status mysql` e log | remover/reinstalar sem backup |
| Backup não rodou | timer do systemd e se o WSL estava ativo | apagar dumps antigos à mão |
| Denodo falha | IP liberado, variáveis, JVM e driver | inventar resultado |
| Indicador ausente | A2 certificado e liberação do piloto | recalcular fora do projeto analítico |
| Recusa por classe | classe da resposta e cliente usado | rebaixar a classe para passar |
| Unicode quebrado | locale/UTF-8 do terminal | regravar fonte sem conferir encoding |
| Link documental falha | `python -m tools.verificar_links` | apontar para arquivo privado |
| Trigger rejeita UPDATE | serviço de versões | desativar trigger |
| RAG não cita | metadados e recuperação | aceitar texto fluente sem fonte |

## 14. T12 — criar ou revisar skill

1. Acrescentar ou editar a entrada da skill em `capacidades/catalogo.yaml` (o texto comum
   está em `capacidades/TEMPLATE_SKILL.md`).
2. Usar ID não reutilizado.
3. Preencher objetivo, entradas, saídas, regras e limites.
4. Vincular fontes metodológicas e dependências.
5. Criar exemplos e testes antes do código, inclusive os casos de teste em outras
   ferramentas de IA (`teste_ia`).
6. Separar cálculo de inferência e definir a classe do dado de cada saída.
7. Revisar privacidade.
8. Rodar `python -m tools.gerar_catalogo_capacidades gerar` e atualizar o cronograma.

## 15. T13 — segurança antes de publicar

```bash
git status --short --untracked-files=all
git diff --check
git log origin/main..HEAD --oneline
detect-secrets scan <arquivos alterados>
python -m tools.security_audit --alvos todos --perfil monorepo --env .env --out artefatos_local/auditoria/pre-push.json
```

Só se publica com a auditoria em `completo_sem_ocorrencia`. Resultados genéricos de busca
exigem revisão manual: placeholders e hashes podem gerar falso positivo. Informar todos os
commits de saída antes de `git push`. Guia completo:
[segurança na publicação](../../ambiente/seguranca-publicacao.md).

## 16. Escalonamento

| Tema | Escalar para |
| --- | --- |
| regra/vigência | analistas e autoridade competente |
| dado pessoal/LGPD | governança/encarregado conforme rito institucional |
| Denodo/rede | TI/Dataprev |
| licença/publicação | administração Microsoft/TI |
| perda/corrupção | responsável técnico, usando backup |
| conflito de fonte | Q5 e `regras_conflitos` |
| indicador divergente | protocolo de validação A1–A5 do projeto analítico |

## 17. Reversão documental

Antes de editar, conferir `git status`; alterações não commitadas podem ser comparadas com
`git diff`. Não usar comandos destrutivos para apagar trabalho do usuário. Arquivos
versionados removidos permanecem recuperáveis pelo histórico, mas a recuperação deve ser
intencional e restrita ao alvo.
