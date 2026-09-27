# Checklist de segurança para publicação

Use esta checklist antes de qualquer commit, push ou abertura de pull request.
O repositório é público; portanto, a revisão de segurança faz parte do fluxo
normal de trabalho.

## 1. Regra principal

Nunca publicar:

- CPF, senha, token, cookie ou qualquer credencial;
- CSV gerado a partir do PETRVS;
- PDF de consulta manual;
- relatório interno de validação;
- script executado localmente com credenciais embutidas;
- caminho local pessoal que revele usuário Windows ou estrutura privada.

## 2. Pastas publicáveis

Podem ser publicadas, após revisão:

```text
README.md
.env.example
docs/
scripts/
```

**Não** devem ser publicadas:

```text
.env e .env.* (exceto .env.example)
*.cnf
.agents/
.claude/
.codex/
instruções de assistente fora da raiz (ex.: agente/AGENTS.md)
artefatos_local/
cgov/
setup/
*.csv
*.pdf
*.ipynb (exceto consultas_denodo_template.ipynb)
```

`CLAUDE.md`, `AGENTS.md` e `PROJECT.md` **da raiz** são públicos desde a
reorganização: têm um núcleo comum sem segredos, dados pessoais ou estado volátil,
mantido por `tools/sincronizar_instrucoes.py`
([sincronia das instruções](../governanca-projeto/sincronia-instrucoes.md)). Precisam
ser arquivos regulares, nunca links para a pasta privada.

> As pastas legadas `Tabelas CSV/` e `Testes PETRVS/` foram migradas para
> `artefatos_local/historico/` em 17.06.2026 e permanecem no `.gitignore`
> por segurança.

## 3. Busca obrigatória por segredos

**Antes de commit:** rode `detect-secrets` nos arquivos alterados.

**Antes de push**, rode a auditoria completa, com o `.env` local e o perfil do
monorepo:

```powershell
python -m tools.security_audit --alvos todos --perfil monorepo --env .env --out artefatos_local/auditoria/pre-push.json
```

- Só se publica com status **`completo_sem_ocorrencia`** (saída 0).
- `completo_com_ocorrencia` (saída 1) e `incompleto` (saída 2) bloqueiam a
  publicação.
- Sem `--env`, o modo de valor exato fica `incompleto`.
- O relatório não contém segredos, mas lista caminhos e linhas: por isso fica no
  acervo privado.

Como checagem rápida e complementar, rode também:

```powershell
rg -n --hidden "PASS|PASSWORD|SENHA|CPF|DENODO_USER|DENODO_PASSWORD|[0-9]{11}|jdbc:denodo" README.md docs scripts .env.example
```

Resultados esperados da checagem rápida:

- `DENODO_USER` e `DENODO_PASSWORD` podem aparecer em instruções e em
  `.env.example`, desde que estejam como placeholders.
- `jdbc:denodo` pode aparecer em código público, desde que a URL seja montada a
  partir de variáveis de ambiente ou use placeholders.
- CPF real, senha real ou caminho local pessoal **não** podem aparecer.

## 4. Verificação do git

Confira os arquivos que entrariam no commit:

```powershell
git status --short
git diff --name-only
```

Se aparecer qualquer arquivo em `artefatos_local/`, `cgov/`, `setup/`, `.env`,
`.agents/`, `.claude/`, `.codex/`, `*.cnf`, `*.csv`, `*.pdf` ou `*.ipynb`, ou
instrução de assistente fora da raiz, não publique.

Se `CLAUDE.md`, `AGENTS.md` ou `PROJECT.md` estiverem na lista, confira a sincronia:
`python -m tools.sincronizar_instrucoes verificar` precisa terminar em estado 1.

## 5. Regras para scripts públicos

Scripts em `scripts/` devem:

- ler credenciais somente de `.env` via `lib/denodo_config.py`;
- usar helpers de `lib/`;
- salvar saídas em `artefatos_local/` (nunca em `scripts/`);
- aceitar `--dry-run` para validar configuração sem conectar ao Denodo;
- não conter CPF, senha ou caminho local pessoal;
- não incorporar linhas reais de CSV ou exemplos com dados pessoais.

## 6. Regras para documentação pública

Documentos em `docs/` podem explicar como configurar o acesso, mas devem usar
apenas exemplos fictícios:

```text
DENODO_USER=seu_cpf_aqui
DENODO_PASSWORD=sua_senha_aqui
DENODO_DRIVER_PATH=C:/Users/SEU_USUARIO/AppData/...
JAVA_HOME=C:/Program Files/DBeaver/jre
```

Não cole trechos de scripts locais, relatórios de validação, documentos do acervo
privado ou CSVs operacionais na documentação pública.

## 7. Ação em caso de vazamento

Se uma credencial real tiver sido commitada:

1. Pare a publicação.
2. Troque ou revogue a credencial imediatamente.
3. Remova o dado do arquivo.
4. Reescreva o histórico apenas se necessário e com procedimento controlado.
5. Rode novamente a busca obrigatória antes de publicar.
