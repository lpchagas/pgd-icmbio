# 06 — Segurança, privacidade e fontes

## 1. Regra de segurança

O protótipo aplica minimização, processamento local e separação por classe. Ter acesso a
uma ferramenta não autoriza inserir nela dados do ICMBio. O controle fica no servidor MCP,
não nas instruções dadas ao cliente: instrução não é controle.

## 2. Classes

| Classe | Exemplos | Local | Modelo local | Cliente externo | Controle |
| --- | --- | --- | --- | --- | --- |
| Público | normas e guias publicados | Sim | Sim | Sim, conferidos termos e vigência | fonte e vigência |
| Sintético | casos de teste das fichas, fixtures | Sim | Sim | Sim | sem derivação de dado real |
| Agregado compartilhável | indicadores do produto compartilhável | Sim | Sim | Sim | k≥5 e supressão complementar |
| Institucional comum | orientações internas não restritas; agregados sem a supressão k≥5 | Sim | Sim | Não | acesso local e logs mínimos |
| Pessoal | nome, contato, resultado individual; produtos nominais do G01/G02 | Restrito | Só o mínimo exigido pela skill | Não | minimização/pseudônimo |
| Sensível | saúde e dados protegidos | Apenas impacto necessário | Apenas categoria/impacto | Não | nunca persistir detalhe clínico |
| Restrito/sigiloso | `99_restrito`, processo protegido | Segregado | Não | Não | fora de Git, RAG e de toda ferramenta MCP |

## 3. Gate de classe no servidor MCP

Decidido na [ADR-014](../../decisoes/ADR-014-llm-execucao-mcp-hibrido.md).

1. Toda resposta de ferramenta leva o campo `classe_dado`.
2. O servidor sabe qual cliente fez a chamada (externo ou modelo local).
3. Se a classe estiver acima do permitido àquele cliente, a resposta é recusada no
   servidor, com erro controlado e log sem conteúdo.
4. Conteúdo `99_restrito` não é servido por nenhuma ferramenta.
5. Na dúvida sobre a classe, vale a mais restritiva.
6. O teste negativo SEC entra no G0 e se repete em cada gate.

Para pôr um serviço externo dentro do gate com conteúdo institucional é preciso nova ADR,
com base institucional (licença e classificação).

## 4. Fluxo antes do processamento

1. Identificar proprietário e finalidade.
2. Classificar o conteúdo.
3. Confirmar se é necessário.
4. Remover campos desnecessários.
5. Escolher o destino permitido pela classe: processamento local, modelo local ou
   cliente externo.
6. Registrar fonte, versão e restrição.
7. Aplicar retenção e descarte adequados.

Na dúvida, tratar como classe mais restritiva e criar pergunta pendente.

## 5. Q5 — fontes institucionais

Q5 continua pendente. O roteiro de fechamento é:

- obter fontes P0 faltantes ou confirmar sua indisponibilidade;
- conferir autenticidade, versão, vigência e alterações;
- executar/revisar OCR onde necessário;
- separar documento de evidência ou transcrição pessoal;
- classificar `tipo_documento` e `natureza` da regra separadamente;
- registrar conflitos;
- validar com analistas;
- registrar ata real;
- atualizar índice e checklist;
- promover fonte quando o S01 estiver operacional.

Até a Q5, o RAG usa só a allowlist pública. Reorganizar arquivos ou escrever esta
proposta não aprova Q5.

## 6. Proveniência

Cada fonte deve informar código, título, emissor, tipo, data, vigência, origem, hash,
classe, status de validação e substituição. Cada regra deve informar natureza, texto
estruturado, fonte/trecho, vigência, versão e confiança de extração.

`tipo_documento` descreve a fonte; `natureza` descreve o significado da regra. Guia ou
curso normalmente produz recomendação/exemplo, não norma.

## 7. Conflitos

Conflitos entram em `regras_conflitos` com regras envolvidas, descrição, impacto, estado e
decisão humana. `documento_substituido_id` é usado somente para substituição integral;
alteração parcial é modelada por versões/vigências próprias.

## 8. RAG seguro

- lista de inclusão, não varredura indiscriminada;
- `99_restrito` excluído;
- metadados de acesso e classe em cada fragmento;
- citação obrigatória;
- revogação/reindexação quando a fonte mudar;
- logs sem conteúdo desnecessário;
- testes de recuperação indevida;
- resposta segura quando a fonte faltar ou conflitar.

## 9. Ferramentas individuais e serviços gratuitos

| Serviço | Uso | Limite de governança |
| --- | --- | --- |
| Claude Code (principal) e Antigravity (secundário) | desenvolvimento e revisão; cliente externo do servidor MCP | plano individual não é API nem licença institucional; só dado público, sintético ou agregado compartilhável |
| Claude Desktop | cliente externo do servidor MCP | mesmas classes do Claude Code |
| Ollama e modelos abertos | redação local sobre institucional comum | conferir a licença do modelo; nada sai do computador |
| Gem (Google AI Pro) com as instruções externas | conversa sobre a metodologia | só conteúdo público ([instruções](../instrucoes-assistente-externo-v1.md)) |
| Gemini free tier | público/sintético, se vigente | não usar conteúdo institucional |
| Microsoft 365 E3 | produtividade do usuário | conferir recurso e política do tenant |
| Power Apps Premium | protótipo individual | distribuição exige licenças adequadas |
| Copilot Studio Viral Trial | experimento | temporário e sem base para produção |
| Fabric/Power Automate (licença gratuita) | experimento individual | não criar dependência crítica |

As condições comerciais e de tratamento mudam; devem ser revalidadas antes de ativação
([AT-02](../recursos-local-first.md)).

## 10. Segredos

Credenciais do Denodo ficam no `.env` local (nomes em `.env.example`); as do MySQL, em
arquivos `.cnf` locais, fora do Git. Exemplos usam nomes de variáveis, nunca valores.
Logs, documentação, prompts e evidências de teste não contêm tokens, senhas, CPFs ou
e-mails reais. Antes de commit, `detect-secrets` nos arquivos alterados; antes de push, a
auditoria de segurança do repositório.

## 11. Retenção e descarte

| Item | Diretriz do protótipo |
| --- | --- |
| Logs técnicos | mínimo necessário, sem conteúdo sensível |
| Logs do gate | cliente, ferramenta, classe e decisão; nunca o conteúdo |
| Execuções de skill | manter rastreabilidade prevista no modelo |
| Dados sintéticos | manter enquanto úteis aos testes |
| Exportações reais | temporárias e controladas |
| Backups | 14 dias, conforme a rotina atual |
| Evidências pessoais | fora do Git e do RAG; retenção institucional a definir |

## 12. Incidente

Ao detectar exposição: interromper o fluxo, preservar evidências mínimas, revogar segredo
se houver, identificar alcance, avisar o responsável apropriado, corrigir a causa (inclusive
a classificação ou o gate) e registrar a decisão. Não copiar o conteúdo exposto para o
relatório do incidente.

## 13. Checklist por gate

- classe definida para toda resposta de ferramenta;
- finalidade e mínimo necessários;
- fonte/vigência conferidas;
- acesso local/externo permitido pela classe;
- teste negativo SEC do gate executado;
- logs revisados;
- retenção definida;
- pessoa responsável identificada;
- pendência registrada quando faltar autorização.
