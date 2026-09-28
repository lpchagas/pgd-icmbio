# Organização público-privado do projeto pgd-icmbio

> **Para quem é este documento:** qualquer pessoa que trabalhe neste projeto — analista, gestor ou técnico — independentemente do nível de familiaridade com Git ou linha de comando.

---

## 1. Por que separar o que é público do que é privado?

Este projeto lida com dados do PETRVS que incluem informações funcionais de servidores públicos. Ao mesmo tempo, a metodologia dos indicadores é um bem público que beneficia todos os órgãos da APF que usam o sistema.

A separação garante que:
- **A metodologia, os scripts e as instruções dos assistentes de IA** (`CLAUDE.md`, `AGENTS.md`, `PROJECT.md`) sejam compartilháveis — ficam no GitHub, sem credenciais nem dados pessoais
- **Suas credenciais de acesso** (CPF e senha do Denodo) jamais apareçam online
- **Os dados extraídos** (CSVs com nomes de unidades e servidores) fiquem fora do repositório
- **As análises internas da CGOV** (ad-hoc, contexto institucional específico) fiquem restritas à pasta privada
- **As skills, as configurações e as memórias locais dos assistentes** (`.agents/`, `.claude/`, `.codex/`) fiquem na pasta privada

---

## 2. O que fica onde

### Repositório público (GitHub — `pgd-ocde-icmbio`, a ser renomeado para `pgd-icmbio`)

Tudo aqui é **versionado e publicável**. Não contém dados pessoais, senhas nem análises internas.

```
C:\Projetos\pgd-icmbio\
├── CLAUDE.md, AGENTS.md, PROJECT.md   Instruções dos assistentes (núcleo comum sincronizado)
├── docs/                         Documentação por assunto (projeto, ambiente, dados-petrvs,
│                                 indicadores, ocde, gestao, relatorios, agente, decisoes…)
├── lib/                          Núcleo compartilhado (Denodo, períodos, escopos, validação)
├── ocde/ gestao/ mgi/            Scripts A1 por família de indicadores
├── relatorios/                   Relatório V2, cumulativo, escopo e privacidade
├── agente/                       Banco local do agente de gestão
├── capacidades/                  Catálogo e especificações S01–S24
├── config/                       Pilotos, conciliações, lock das instruções
├── tools/                        Auditoria, pilotos, aceites, replay, links, sincronia, skills
├── tests/                        Testes automatizados (não abrem o Denodo)
├── .env.example                  Modelo do .env — sem senhas reais
├── consultas_denodo_template.ipynb  Notebook público sem credenciais
└── README.md
```

### Pasta privada (sincronizada — `pgd-ocde-icmbio-privado`)

Tudo aqui é **local e sincronizado via nuvem**, com acesso restrito à equipe do projeto. Nunca vai para o GitHub. Hoje a pasta fica no OneDrive; a migração para uma biblioteca SharePoint do ICMBio está prevista. O caminho é informado pela variável `PGD_PRIVADO_DIR` (sem ela, vale o caminho do OneDrive abaixo).

```
C:\Users\<SEU_USUARIO>\OneDrive - ICMBio\projetos\pgd-ocde-icmbio-privado\
├── artefatos_local/
│   ├── ocde/
│   │   ├── entregas/YYYY-MM/escopos/<scope-key>/  CSVs mensais OCDE por escopo
│   │   ├── relatorios_v2/YYYY-MM/escopos/<scope-key>/  relatórios finais e manifestos
│   │   └── diagnosticos/YYYY-MM/ Scripts A4 e CSVs de diagnóstico interno
│   ├── gestao/YYYY-MM/escopos/<scope-key>/  A2 de G01/G02 e anexos restritos
│   ├── validacao/YYYY-MM/escopos/<scope-key>/  A3–A5 e manifestos por escopo
│   ├── validacao/                baselines, aceites e documentos deliberativos da CGOV
│   ├── sincronia/                diário da sincronia das instruções
│   ├── docs_internos/            Documentação local não publicável
│   ├── historico/                Artefatos de fases anteriores
│   └── backup_scripts_a1/        Cópias de segurança dos scripts A1
├── cgov/                         Análises internas CGOV (privadas)
│   └── analises/
│       └── objetivos_processos/  I03 enriquecido com objetivos e cadeia de valor
├── setup/                        Scripts de configuração de ambiente local
│   ├── configurar_env.ps1        Gera .env com caminhos desta máquina
│   └── criar_links_privados.ps1  Recria as junções em outro computador
└── assistentes/
    ├── .claude/                  Configurações locais do Claude Code
    ├── .codex/                   Configurações locais do Codex
    └── .agents/                  Skills (fonte canônica) e manifesto das skills
```

> Cópias antigas de `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` que ainda estejam em `assistentes\` são só histórico: desde a reorganização, a versão vigente é a do Git.

### Documentos deliberativos da CGOV (regra de 13.09.2026)

Cadernos metodológicos, registros de decisão de homologação e atas da CGOV são
**sempre privados** e ficam em `artefatos_local/validacao/`, com nome no padrão
`caderno-metodologico-cgov-vN_DD.MM.AAAA.md`. Nunca são gravados em `docs/`.

A documentação pública pode citar o identificador da decisão (D01, D02…) e o efeito
técnico que ela produziu no código, mas não reproduz a deliberação nem aponta links
para o acervo privado.

Desde a D18, o anexo nominal do G02 é autorizado somente no produto restrito e para
finalidade gerencial. Ele permanece em `artefatos_local/`, nunca em `docs/` ou no
GitHub, e não contém CPF, e-mail, telefone ou endereço.

### O que fica apenas local (nem GitHub, nem pasta privada)

| Arquivo | Por que não vai a lugar nenhum |
|---------|-------------------------------|
| `.env` | Contém sua senha em texto puro — **nunca** sincronizar na nuvem |
| `*.cnf` do MySQL do agente | Credenciais do banco local |

> **Recomendação de segurança:** armazene sua senha do Denodo em um gerenciador de senhas (Bitwarden, KeePass, 1Password). Assim, mesmo que precise reconfigurar o `.env`, a senha está disponível com segurança.

---

## 3. Como o VS Code "enxerga" tudo junto

Na pasta do projeto você verá as pastas `artefatos_local`, `cgov`, `setup`, `.claude`, `.codex` e `.agents` como se estivessem ali. Elas são **junções** (Junctions do Windows) que apontam para a pasta privada. Os arquivos `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` **não** são pontes: são arquivos regulares, versionados no Git.

```
C:\Projetos\pgd-icmbio\
├── artefatos_local  →→→ [junção] →→→ <pasta privada>\artefatos_local
├── cgov             →→→ [junção] →→→ <pasta privada>\cgov
├── setup            →→→ [junção] →→→ <pasta privada>\setup
├── .claude          →→→ [junção] →→→ <pasta privada>\assistentes\.claude
├── .codex           →→→ [junção] →→→ <pasta privada>\assistentes\.codex
└── .agents          →→→ [junção] →→→ <pasta privada>\assistentes\.agents
```

Do ponto de vista do VS Code e dos scripts Python, é como se tudo estivesse na mesma pasta. O Git, porém, ignora essas junções (o `.gitignore` as lista explicitamente).

**Links das skills.** Cada skill aparece para o Claude Code em `.claude\skills\<nome>`, por meio de uma junção para `.agents\skills\<nome>`. Esses links são **locais de cada computador**: o OneDrive não os sincroniza (ficam como "Sync pending"), então cada computador os recria com o instalador (Passo 4 da seção 4).

---

## 4. Configurar outro computador da equipe

Ao trabalhar em uma máquina diferente pela primeira vez, siga esta sequência:

### Passo 1 — Clonar o repositório

```powershell
git clone https://github.com/lpchagas/pgd-ocde-icmbio "C:\Projetos\pgd-icmbio"
cd "C:\Projetos\pgd-icmbio"
```

### Passo 2 — Aguardar a pasta privada sincronizar

Verifique se a pasta `pgd-ocde-icmbio-privado` aparece em:
`C:\Users\SEU_USUARIO\OneDrive - ICMBio\projetos\`

O ícone do OneDrive na bandeja do sistema deve mostrar sincronização concluída (sem seta de refresh). Se a pasta privada estiver em outro lugar (por exemplo, numa biblioteca SharePoint sincronizada), defina a variável `PGD_PRIVADO_DIR` com o caminho dela antes do passo 3.

### Passo 3 — Criar as junções

```powershell
.\setup\criar_links_privados.ps1
```

Este script cria **só junções de pastas** — `artefatos_local`, `cgov`, `setup`, `.claude`, `.codex` e `.agents` — e confere que `CLAUDE.md`, `AGENTS.md` e `PROJECT.md` são arquivos regulares. Se encontrar um link antigo (por exemplo, criado pelo WSL, que o Windows não enxerga), pergunta antes de substituí-lo; a substituição remove só o link, nunca o conteúdo.

> Como a pasta `setup` também é uma junção, na primeira instalação ela ainda não existe no projeto. Execute o script a partir da pasta privada, informando o projeto:
>
> ```powershell
> & "$env:USERPROFILE\OneDrive - ICMBio\projetos\pgd-ocde-icmbio-privado\setup\criar_links_privados.ps1" -Projeto "C:\Projetos\pgd-icmbio"
> ```
>
> O script recusa pasta que não seja a raiz do repositório (sem `.git`).

### Passo 4 — Criar os links das skills

```powershell
python -m tools.skills_manager install --apply
```

Cria uma junção por skill em `.claude\skills` (no Linux ou num contêiner, um symlink). É idempotente: pode ser executado de novo sem efeito colateral.

### Passo 5 — Gerar o `.env` desta máquina

```powershell
.\setup\configurar_env.ps1
```

O script detecta automaticamente o nome de usuário Windows e o caminho do driver Denodo instalado pelo DBeaver. Ao final, abre instruções para você preencher apenas CPF e senha.

### Passo 6 — Instalar dependências Python

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-report.txt -r requirements-dev.txt
```

As dependências do agente ficam em `requirements-agente.txt`.

### Passo 7 — Testar a conexão

```powershell
.venv\Scripts\python.exe ocde/indicadores/IND_OCDE_02.1_run.py --data-execucao AAAA-MM-DD
```

Se retornar dados, o ambiente está configurado corretamente. O acesso depende de o IP da máquina estar liberado pelo Dataprev.

---

## 5. O `.env` em mais de um computador

Os scripts Python leem **todos** os caminhos do arquivo `.env`, então não há nada hardcoded no código. Mas o `.env` precisa ser ajustado para cada máquina porque:

| Variável | Por que muda entre máquinas |
|----------|----------------------------|
| `DENODO_USER` | Credencial individual de cada pessoa da equipe |
| `DENODO_PASSWORD` | Credencial individual de cada pessoa da equipe |
| `JAVA_HOME` | Geralmente igual, mas pode variar se o DBeaver foi instalado fora do caminho padrão |
| `DENODO_DRIVER_PATH` | **Muda sempre** — depende do nome de usuário Windows e do número de versão do driver (ex.: `/9/` pode virar `/10/` após atualização do DBeaver) |

**O `configurar_env.ps1` resolve isso automaticamente** — ele busca o caminho correto do driver na máquina atual, independentemente do nome de usuário ou versão do driver.

### O que é compartilhado entre os computadores

| Item | Compartilhado? | Como |
|------|----------------|------|
| Scripts e módulos (`ocde/`, `gestao/`, `lib/`, `relatorios/`, `tools/`) | Sim | Git (`git pull`) |
| Documentação (`docs/`) | Sim | Git (`git pull`) |
| Instruções dos assistentes (`CLAUDE.md`, `AGENTS.md`, `PROJECT.md`) | Sim | Git (`git pull`) |
| Análises CGOV (`cgov/`) | Sim | Pasta privada (automático) |
| Scripts de setup (`setup/`) | Sim | Pasta privada (automático) |
| CSVs mensais (`artefatos_local/ocde/entregas/`) | Sim | Pasta privada (automático) |
| Diagnósticos, relatórios e aceites | Sim | Pasta privada (automático) |
| Skills e configurações dos assistentes (`.agents/`, `.claude/`, `.codex/`) | Sim | Pasta privada (automático) |
| Links das skills (`.claude\skills\<nome>`) | **Não** | Recriados em cada computador pelo instalador |
| `.env` com credenciais | **Não** | Cada máquina tem o seu próprio |

---

## 6. Rotina de trabalho recomendada

### Ao começar a trabalhar

```
1. git pull                          → código, documentação e instruções atualizados
2. Aguardar a pasta privada sincronizar → artefatos, cgov e skills disponíveis
3. Verificar .env presente           → se não, rodar configurar_env.ps1
```

### Ao terminar o trabalho

```
1. Se editou CLAUDE.md, AGENTS.md ou PROJECT.md:
   python -m tools.sincronizar_instrucoes sincronizar
2. git add / git commit / git push   → apenas arquivos públicos
   [o .gitignore bloqueia tudo que for sensível]
3. A pasta privada sincroniza automaticamente → artefatos e análises ficam disponíveis para a equipe
```

### O que NUNCA fazer

- `git add .env` — bloqueado pelo .gitignore, mas nunca forçar
- `git add cgov/` — análises CGOV são privadas; ficam na pasta privada
- Criar instruções de assistente em subpastas (ex.: `agente/AGENTS.md`, que fica fora do Git) — só as da raiz são permitidas
- Copiar credenciais nos comentários de commit ou nos nomes de arquivo
- Mover CSVs para dentro de `docs/` ou `ocde/` — essas pastas são públicas
- Colocar o `.env` na pasta privada — senha em texto puro na nuvem é risco desnecessário

---

## 7. Cuidados com LGPD e dados pessoais

Os CSVs gerados pelos scripts de indicadores podem conter:
- Siglas e nomes de unidades organizacionais
- Contagens de servidores por unidade
- Médias de avaliação por unidade

Esses dados são **funcionais e institucionais**, não nominais. Ainda assim:

- Mantenha-os em `artefatos_local/` (pasta privada — nunca no GitHub)
- Ao compartilhar resultados por e-mail ou apresentação, exporte apenas tabelas agregadas
- Nunca inclua CPFs nos CSVs de entrega (as queries não expõem CPF individualmente, apenas contagens)
- O acesso ao Denodo (que contém dados nominais completos) é protegido por CPF + senha individual e IP liberado pelo Dataprev

---

## 8. Diferença entre as três camadas de armazenamento

| Camada | O que vai | Quem acessa | Voltado para |
|--------|-----------|-------------|--------------|
| **GitHub** (público) | Código, documentação, instruções dos assistentes, templates | Qualquer pessoa | Replicação por outros órgãos da APF |
| **Pasta privada** (nuvem, acesso restrito) | Artefatos, `cgov/`, skills e configurações dos assistentes, resultados | Equipe do projeto | Continuidade entre computadores e pessoas da equipe |
| **Local apenas** | `.env` e `*.cnf` com credenciais; links das skills | Só você, nesta máquina | Segurança — senha não vai a lugar nenhum |

---

## 9. Proteção contra perda acidental e backup de redundância

### Por que isso importa

A pasta `OneDrive - ICMBio\projetos\` contém a pasta privada à qual as junções do projeto apontam. Se ela for apagada ou movida acidentalmente, todas as 6 junções do projeto ficam quebradas e as pastas `artefatos_local`, `cgov`, `setup`, `.claude`, `.codex` e `.agents` aparecem vazias.

O OneDrive recupera arquivos deletados da lixeira da nuvem (por até 93 dias), mas a resincronização pode levar horas. Para minimizar o risco, duas medidas preventivas estão em vigor:

### Medida 1 — Arquivo sentinela

Um arquivo `LEIA-ME_NAO_DELETAR.txt` fica na raiz de `OneDrive - ICMBio\projetos\`. Ele serve de alerta visual antes de qualquer deleção acidental no Explorer ou no OneDrive web.

Para conferir se a pasta privada continua acessível:

```powershell
.\setup\criar_links_privados.ps1   # verifica se a pasta privada existe
```

### Medida 2 — Backup de redundância no Google Drive

O script `setup\backup_privado.ps1` copia incrementalmente as partes não regeneráveis do projeto para o Google Drive, criando uma segunda cópia independente do OneDrive ICMBio.

**O que é copiado:**

| Pasta | Conteúdo | Por que incluir |
| --- | --- | --- |
| `assistentes\` | `.agents\` (skills e manifesto), `.claude\`, `.codex\` | Não versionado no Git |
| `cgov\` | Análises internas CGOV | Privadas e únicas |
| `setup\` | configurar_env.ps1, criar_links_privados.ps1 | Scripts de recuperação do ambiente |
| `artefatos_local\validacao\` | A3–A5, baselines, aceites e documentos deliberativos da CGOV | Caderno metodológico e decisões são registro institucional — não regeneráveis |
| `artefatos_local\ocde\diagnosticos\` | Scripts A4 e CSVs de diagnóstico | Registro de investigações — não regenerável |
| `artefatos_local\docs_internos\` | Documentação local | Não versionada |
| `artefatos_local\historico\` | Artefatos de fases anteriores | Referência histórica |

**O que NÃO é copiado (economiza espaço — regenerável):**

| Pasta | Por que excluir |
| --- | --- |
| `artefatos_local\ocde\entregas\` | CSVs mensais dos 12 indicadores — regeneráveis via `python -m lib.indicator_extraction` |
| `artefatos_local\ocde\analises\` | Gráficos PNG — regeneráveis via `/graficos-gerenciais` |
| `artefatos_local\ocde\relatorios\` | Relatórios Markdown — regeneráveis via `/relatorio-gerencial` |

**Como executar:**

```powershell
.\setup\backup_privado.ps1
```

O script usa `robocopy` (nativo do Windows) com cópia incremental — só sincroniza o que mudou, sem duplicar dados desnecessariamente.

**Quando executar:**

- Após validar e salvar relatórios A5 importantes
- Após alterar skills ou configurações locais dos assistentes
- **Antes de reorganizar pastas no OneDrive** ← evita exatamente o incidente que motivou esta seção
- Semanalmente como rotina preventiva

### Recuperação em caso de perda

Se a pasta `projetos\` for deletada do OneDrive:

1. **Recuperar do Google Drive** (imediato): a pasta `My Drive\_projetos\pgd-ocde-icmbio-privado\` contém a última cópia do backup.
2. **Copiar de volta para o OneDrive**: restaurar manualmente para `OneDrive - ICMBio\projetos\pgd-ocde-icmbio-privado\`.
3. **Aguardar sincronização** do OneDrive.
4. **Recriar as junções**: `.\setup\criar_links_privados.ps1`
5. **Recriar os links das skills**: `python -m tools.skills_manager install --apply`
6. **Restaurar os CSVs de entregas** (se necessário): reexecutar a extração com `--data-execucao` — os dados vêm do Denodo em tempo real.

---

## 10. Resolução de problemas comuns

### "As pastas `artefatos_local`, `cgov`, `.claude` etc. aparecem vazias após clonar o repositório"

Normal — elas não são versionadas no Git. Execute `criar_links_privados.ps1` para recriar as junções com a pasta privada.

### "As skills do projeto não aparecem no assistente"

Os links de `.claude\skills` são locais e podem estar ausentes ou ser links antigos do WSL, invisíveis no Windows. Rode `python -m tools.skills_manager install --apply` e abra uma nova sessão. Para conferir o pacote das skills: `python -m tools.skills_manager validate`.

### "A pasta `cgov` não foi criada pelo script de links"

O script exibe `IGNORADO (cgov): destino nao existe ainda` se a pasta `cgov/` ainda não existir na pasta privada. Nesse caso:

1. Crie a estrutura manualmente na pasta privada:

   ```powershell
   New-Item -ItemType Directory "$env:USERPROFILE\OneDrive - ICMBio\projetos\pgd-ocde-icmbio-privado\cgov\analises\objetivos_processos" -Force
   ```

2. Aguarde a sincronização
3. Execute `criar_links_privados.ps1` novamente

### "O script Python falha com erro de driver JAR"

O `DENODO_DRIVER_PATH` no `.env` está errado para esta máquina. Execute `configurar_env.ps1` novamente para detectar o caminho correto.

### "O DBeaver atualizou e os scripts pararam de funcionar"

O número de versão do driver mudou (ex.: de `/9/` para `/10/`). Execute `configurar_env.ps1` — ele detecta automaticamente o novo caminho. Lembre também de copiar o arquivo sem extensão como `.jar`, conforme o guia de [acesso ao Denodo e DBeaver](acesso-denodo-dbeaver.md).

### "Não encontro a pasta OneDrive - ICMBio no meu computador"

O OneDrive pode ter um nome diferente nesta máquina (ex.: apenas "OneDrive"), ou a pasta privada pode estar numa biblioteca SharePoint. Defina a variável `PGD_PRIVADO_DIR` com o caminho correto da pasta privada e execute o script de novo:

```powershell
$env:PGD_PRIVADO_DIR = "C:\caminho\da\pasta\pgd-ocde-icmbio-privado"
.\setup\criar_links_privados.ps1
```
