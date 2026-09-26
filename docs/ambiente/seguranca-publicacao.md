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
.env
CLAUDE.md
.claude/
artefatos_local/
*.csv
*.pdf
*.ipynb
```

> As pastas legadas `Tabelas CSV/` e `Testes PETRVS/` foram migradas para
> `artefatos_local/historico/` em 17.06.2026 e permanecem no `.gitignore`
> por segurança.

## 3. Busca obrigatória por segredos

Rode a busca abaixo antes de publicar:

```powershell
rg -n --hidden "PASS|PASSWORD|SENHA|CPF|DENODO_USER|DENODO_PASSWORD|[0-9]{11}|jdbc:denodo" README.md docs scripts .env.example
```

Resultados esperados:

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

Se aparecer qualquer arquivo em `artefatos_local/`, `.env`, `.claude/`,
`*.csv`, `*.pdf` ou `*.ipynb`, não publique.

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

Não cole trechos de `CLAUDE.md`, scripts locais, relatórios de validação ou
CSVs operacionais na documentação pública.

## 7. Ação em caso de vazamento

Se uma credencial real tiver sido commitada:

1. Pare a publicação.
2. Troque ou revogue a credencial imediatamente.
3. Remova o dado do arquivo.
4. Reescreva o histórico apenas se necessário e com procedimento controlado.
5. Rode novamente a busca obrigatória antes de publicar.
