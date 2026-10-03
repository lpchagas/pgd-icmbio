# Acesso ao PETRVS via Denodo no DBeaver

Este guia cobre a configuração da conexão com o banco `petrvs_icmbio` pelo Denodo, usando o DBeaver como ferramenta de consulta, e as primeiras validações após a conexão.

**Perfil:** analista ou técnico que vai executar as consultas SQL. Se você é gestor buscando interpretar os resultados sem SQL, consulte [08-guia-rapido-gestores.md](../indicadores/guia-rapido-gestores.md).

---

## O que é o Denodo

O Denodo é uma ferramenta de virtualização de dados operada pelo Dataprev. Ele entrega os dados do PETRVS em tempo real, sem necessidade de restaurar dumps locais ou manter MySQL instalado na máquina. A conexão é feita pela internet, com autenticação individual.

---

## 1. Pré-requisitos

Antes de começar, confirme:

- [ ] Você recebeu credenciais de acesso ao Denodo do responsável pelo projeto no seu órgão
- [ ] O IP da sua máquina ou rede foi liberado pelo Dataprev (conexões de IPs não autorizados são bloqueadas silenciosamente)
- [ ] O DBeaver Community está instalado ([dbeaver.io/download](https://dbeaver.io/download/))

Se o seu IP ainda não foi liberado, entre em contato com o gestor responsável pela solicitação ao Dataprev antes de prosseguir.

---

## 2. Instalar o DBeaver

Caso ainda não tenha instalado:

1. Acesse [dbeaver.io/download](https://dbeaver.io/download/) e baixe a versão **Community** (gratuita).
2. Execute o instalador normalmente no Windows.
3. Abra o programa.

---

## 3. Criar a conexão Denodo no DBeaver

1. Clique no ícone de **tomada** no canto superior esquerdo (`New Database Connection`).
2. Na caixa de busca, digite `denodo` e selecione o driver **Denodo**.
3. Clique em **Next**.
4. Preencha os campos:

   | Campo | Valor |
   | --- | --- |
   | Host | `denodo-pgd.dataprev.gov.br` |
   | Port | `443` |
   | Database/Schema | `petrvs_icmbio` |
   | Username | credencial fornecida pelo gestor responsável |
   | Password | credencial fornecida pelo gestor responsável |

5. Marque **Save password** para não precisar digitar toda vez.

---

## 4. Instalar o driver Denodo

Na primeira conexão, o DBeaver detecta que o driver Denodo não está instalado e abre um popup de download automático:

1. Clique na aba **Driver Properties** (o DBeaver acusa um triângulo amarelo de aviso).
2. O popup **Download driver files** aparece automaticamente.
3. Clique em **Download** e aguarde.

Se o teste de conexão acusar `Class not found: com.denodo.vdp.jdbc.Driver`, o download automático trouxe o pacote errado: ver "O DBeaver não encontra o driver Denodo" na seção 8 (Problemas comuns).

Se o popup não aparecer, ou se você cancelar acidentalmente:

- Feche a janela de configuração sem salvar.
- Recomece o processo desde o passo 1 — o popup reaparecerá.

---

## 5. Testar a conexão

1. Com os dados preenchidos, clique em **Test Connection** (canto inferior esquerdo).
2. O resultado esperado é: **Connected** — com o servidor `Virtual DataPort 9.x` e o driver `com.denodo.vdp.jdbc.Driver`.
3. Se conectou, clique em **Ok** e depois em **Finish**.

A conexão aparece no painel **Database Navigator** com o nome que você definiu.

---

## 6. Primeiras consultas de validação

Abra um SQL Editor (botão direito na conexão > `SQL Editor` > `New SQL Script`) e execute as consultas abaixo para confirmar que os dados estão acessíveis.

**Listar tabelas disponíveis:**

```sql
select * from get_views();
```

**Contar entregas ativas:**

```sql
select count(*) as total_entregas_ativas
from petrvs_icmbio_planos_entregas_entregas
where deleted_at is null;
```

**Contar unidades ativas:**

```sql
select count(*) as total_unidades
from petrvs_icmbio_unidades
where deleted_at is null;
```

**Exploração inicial das entregas:**

```sql
select
    id,
    descricao,
    descricao_entrega,
    coalesce(nullif(trim(descricao), ''), nullif(trim(descricao_entrega), '')) as nome_entrega
from petrvs_icmbio_planos_entregas_entregas
limit 200;
```

---

## 7. Próximo passo

Com o ambiente validado, execute os indicadores OCDE/PGD seguindo [docs/06-indicadores-ocde-denodo.md](../ocde/06-indicadores-ocde-denodo.md).

---

## 8. Problemas comuns

### Erro de conexão sem mensagem clara

Causa mais provável: o IP da sua máquina não está liberado no Denodo. Verifique com o gestor responsável se o seu IP (fixo) foi cadastrado pelo Dataprev.

### O DBeaver não encontra o driver Denodo

O Denodo não é um banco convencional — o DBeaver baixa o driver na primeira conexão. Se o download falhar, verifique o acesso à internet e tente novamente. O driver também pode ser baixado manualmente na página de drivers JDBC da Denodo, [community.denodo.com/drivers/jdbc/9](https://community.denodo.com/drivers/jdbc/9): escolha o download **JDBC** (`denodo-vdp-jdbcdriver-9.x.jar`).

Atenção: o endereço direto `community.denodo.com/drivers/jdbc/9/denodo-vdp-jdbcdriver`, usado também pelo download automático do DBeaver, passou a entregar o pacote **ODBC** para Windows (`denodo-vdp-odbcdriver-...-win.zip`, dezenas de MB). Sintoma no DBeaver: `Can't create driver instance` com `Class not found: com.denodo.vdp.jdbc.Driver`. Correção:

1. Baixe o `.jar` JDBC pela página acima e guarde-o numa pasta fixa (ex.: `C:\Users\<usuário>\drivers\denodo\`).
2. Em **Database → Driver Manager → Denodo → Edit... → Libraries**, remova o item atual e use **Add File** para apontar o `.jar`.
3. Se o DBeaver oferecer **Download driver files** de novo, cancele.

Nesse caso, use o mesmo `.jar` em `DENODO_DRIVER_PATH` (seção seguinte), sem a cópia do arquivo baixado pelo DBeaver.

### Os scripts Python não encontram o driver (`.jar`)

Os scripts (JPype/JDBC) usam o mesmo driver que o DBeaver baixou, mas o DBeaver o grava **sem extensão**. Crie uma cópia com extensão `.jar` — e repita depois de cada atualização do driver pelo DBeaver:

```powershell
$dir = "$env:APPDATA\DBeaverData\drivers\remote\drivers\jdbc\9"
Copy-Item "$dir\denodo-vdp-jdbcdriver" "$dir\denodo-vdp-jdbcdriver.jar" -Force
```

O caminho da cópia vai para `DENODO_DRIVER_PATH` no `.env` (o `setup\configurar_env.ps1`, privado, detecta-o automaticamente).

### Erro de autenticação (usuário/senha inválidos)

Confirme com o gestor responsável se suas credenciais estão ativas. Credenciais do Denodo são individuais e fornecidas pelo responsável do projeto em cada órgão.

### A conexão funciona mas não aparecem tabelas

Verifique se o **Database/Schema** está definido como `petrvs_icmbio`. Se estiver em branco, o DBeaver conecta no servidor mas não filtra o schema correto.
