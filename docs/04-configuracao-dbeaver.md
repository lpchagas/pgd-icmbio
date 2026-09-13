# Configuração do DBeaver para este projeto

Este documento cobre as configurações do DBeaver para trabalhar com o banco `petrvs_icmbio` via Denodo.

---

## 1. Configurações da conexão Denodo

Para editar uma conexão existente, clique com o botão direito nela no **Database Navigator** e escolha **Edit Connection**.

### Aba Principal (Main)

| Campo | Valor |
| --- | --- |
| Host | `denodo-pgd.dataprev.gov.br` |
| Port | `443` |
| Database/Schema | `petrvs_icmbio` |
| Username | credencial individual fornecida pelo gestor |
| Password | credencial individual fornecida pelo gestor |

Marque **Save password** para não precisar digitar toda vez.

### Aba Driver Properties

Normalmente não é necessário alterar nada. Se aparecer erro de SSL ou certificado:

| Propriedade | Valor |
| --- | --- |
| `useSSL` | `true` |
| `trustServerCertificate` | `true` |

---

## 2. Como abrir um SQL Editor

1. Clique com o botão direito na conexão Denodo no Database Navigator.
2. Clique em `SQL Editor`.
3. Clique em `New SQL Script`.

Ou use o atalho `Ctrl+]` com a conexão selecionada.

---

## 3. Como executar uma consulta

- `Ctrl+Enter` executa o bloco onde o cursor está (ou a seleção, se houver).
- `Ctrl+A` + `Ctrl+Enter` executa o script inteiro.
- Para os indicadores deste projeto: **sempre execute a query completa** — as CTEs são encadeadas e não funcionam executadas em partes.

---

## 4. Como exportar resultado para planilha

Após executar a consulta:

1. Clique com o botão direito no grid de resultados.
2. Clique em `Export Results`.
3. Escolha `CSV` ou `XLSX`.
4. Siga o assistente e escolha a pasta de destino.

Salve os CSVs na pasta privada `artefatos_local/` (que está no `.gitignore` e não vai para o GitHub).

---

## 5. Como salvar uma consulta como arquivo SQL

1. No editor SQL aberto, pressione `Ctrl+S`.
2. Escolha um nome e pasta.
3. O arquivo é salvo como `.sql` e pode ser reaberto depois.

---

## 6. Como trabalhar com múltiplas abas

O DBeaver permite abrir várias abas de SQL Editor ao mesmo tempo. Isso é útil para:

- Executar uma consulta de auditoria em uma aba e o indicador em outra.
- Comparar resultados lado a lado.

Use `Ctrl+]` repetidamente para abrir novas abas.

---

## 7. Nota sobre CTEs recursivas (I07 e I08)

Os indicadores I07 e I08 usam CTEs recursivas para gerar o calendário de dias úteis. O comando `SET SESSION cte_max_recursion_depth`, específico do MySQL, **não se aplica ao Denodo**.

Se as queries de I07 e I08 apresentarem erro de profundidade de recursão no Denodo, consulte [docs/06.3.3-i07.md](ocde/06.3.3-i07.md) para a versão adaptada da query.

---

## 8. Vantagens do DBeaver para este projeto

- Suporta conexão Denodo com download automático de driver.
- Exporta resultados para CSV/XLSX sem instalar nada adicional.
- Permite abrir e comparar vários scripts ao mesmo tempo.
- Visualiza estrutura das tabelas graficamente (diagrama ER).
- Funciona de forma idêntica em Windows, macOS e Linux.
