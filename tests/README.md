# Suíte de testes automatizados — pgd-ocde-icmbio

Protocolo de verificação de código complementar ao processo humano CGOV
(`docs/09-protocolo-validacao-indicadores.md`). Ver seção "Divisão de
responsabilidade" abaixo.

## Como rodar

```powershell
cd C:\Projetos\pgd-ocde-icmbio
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt   # uma vez
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```

Ou via skill: `/verificar-consistencia`.

## Marcadores (`pytest.ini_options.markers` em `pyproject.toml`)

| Marcador | O que cobre | Depende de rede/Denodo? |
| --- | --- | --- |
| `unit` | Funções puras de `lib/` e `ocde/relatorios/` — períodos, CSV, semáforos, métricas | Não |
| `regression` | Bugs históricos documentados (escala Eixo 4, unidade I07/I08) + sanidade de documentação | Não |
| `integration` | Execução real contra o Denodo (não existe hoje — reservado) | Sim — **skip por padrão** (`addopts = "not integration"`) |

## Divisão de responsabilidade: automação × deliberação institucional

- Os testes offline verificam sintaxe, contratos, regressões históricas, fórmulas
  independentes, propriedades, privacidade e a janela temporal.
- A validação integrada compara A1 e A3 com extrações atômicas somente leitura do
  Denodo. Indisponibilidade externa não é convertida em sucesso.
- A CGOV homologa a definição de negócio e decide exceções. Fixture sintética e
  convergência numérica não substituem essa deliberação.

O protocolo e os estados permitidos estão em
[`docs/09-protocolo-validacao-indicadores.md`](../docs/09-protocolo-validacao-indicadores.md).
Os checks do GitHub não dependem de arquivos privados, Denodo ou artefatos locais.

## Por que não há mock de JDBC/jpype

Mockar `ResultSet`, `Statement` e a conexão testaria a simulação, não a semântica
da consulta Denodo. As fórmulas são exercitadas com fixtures sintéticas e a
compatibilidade real é verificada no gate integrado, fora da integração contínua.

## Estrutura

```
tests/
  conftest.py                    fixtures compartilhadas (project_root, fixtures_dir)
  unit/                           testes de funções puras, sem I/O externo
  regression/                     regressão de bugs históricos + sanidade de docs
  integration/                    reservado para testes contra Denodo real (skip por padrão)
  fixtures/
    csv_bons/                     CSVs sintéticos válidos
    csv_corrompidos/               CSVs sintéticos com defeitos propositais
    docs_sql_sinteticos/           docs .md sintéticos para lib/docs_sql.py
```
