# 06 — Segurança, privacidade e fontes

## 1. Regra de segurança

O protótipo aplica minimização, processamento local e separação por classe. Ter acesso a
uma ferramenta não autoriza inserir nela dados do ICMBio.

## 2. Classes

| Classe | Exemplos | Local | Externo | Controle |
| --- | --- | --- | --- | --- |
| Público | normas e guias publicados | Sim | Condicional | conferir termos e vigência |
| Institucional comum | orientações internas não restritas | Sim | Não no protótipo | acesso local e logs mínimos |
| Pessoal | nome, contato, resultado individual | Restrito | Não | minimização/pseudônimo |
| Sensível | saúde e dados protegidos | Apenas impacto necessário | Não | nunca persistir detalhe clínico |
| Restrito/sigiloso | `99_restrito`, processo protegido | Segregado | Não | exclusão de RAG e Git |

## 3. Fluxo antes do processamento

1. Identificar proprietário e finalidade.
2. Classificar o conteúdo.
3. Confirmar se é necessário.
4. Remover campos desnecessários.
5. Escolher processamento local ou externo permitido.
6. Registrar fonte, versão e restrição.
7. Aplicar retenção e descarte adequados.

Na dúvida, tratar como classe mais restritiva e criar pergunta pendente.

## 4. Q5 — fontes institucionais

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
- promover fonte quando S01 estiver operacional.

Reorganizar arquivos ou escrever esta proposta não aprova Q5.

## 5. Proveniência

Cada fonte deve informar código, título, emissor, tipo, data, vigência, origem, hash,
classe, status de validação e substituição. Cada regra deve informar natureza, texto
estruturado, fonte/trecho, vigência, versão e confiança de extração.

`tipo_documento` descreve a fonte; `natureza` descreve o significado da regra. Guia ou
curso normalmente produz recomendação/exemplo, não norma.

## 6. Conflitos

Conflitos entram em `regras_conflitos` com regras envolvidas, descrição, impacto, estado e
decisão humana. `documento_substituido_id` é usado somente para substituição integral;
alteração parcial é modelada por versões/vigências próprias.

## 7. RAG seguro

- lista de inclusão, não varredura indiscriminada;
- `99_restrito` excluído;
- metadados de acesso em cada fragmento;
- citação obrigatória;
- revogação/reindexação quando fonte mudar;
- logs sem conteúdo desnecessário;
- testes de recuperação indevida;
- resposta segura quando fonte faltar ou conflitar.

## 8. Ferramentas individuais e serviços gratuitos

| Serviço | Uso | Limite de governança |
| --- | --- | --- |
| Assistentes de programação (Codex, Claude Code) | desenvolvimento e revisão | plano individual não é API nem licença institucional; uso multiusuário é separado |
| Gemini free tier | público/sintético, se vigente | não usar conteúdo institucional |
| Microsoft 365 E3 | produtividade do usuário | conferir recurso e política do tenant |
| Power Apps Premium | protótipo individual | distribuição exige licenças adequadas |
| Copilot Studio Viral Trial | experimento | temporário e sem base para produção |
| Fabric/Power Automate (licença gratuita) | experimento individual | não criar dependência crítica |

As condições comerciais e de tratamento mudam; devem ser revalidadas antes de ativação.

## 9. Segredos

Credenciais ficam em `.env` e `.cnf` ignorados. Exemplos usam nomes de variáveis, nunca
valores. Logs, documentação, prompts e evidências de teste não contêm tokens, senhas,
CPFs ou e-mails reais.

## 10. Retenção e descarte

| Item | Diretriz do protótipo |
| --- | --- |
| Logs técnicos | mínimo necessário, sem conteúdo sensível |
| Execuções de skill | manter rastreabilidade prevista no modelo |
| Dados sintéticos | manter enquanto úteis aos testes |
| Exportações reais | temporárias e controladas |
| Backups | 14 dias conforme rotina atual |
| Evidências pessoais | fora do Git e do RAG; retenção institucional a definir |

## 11. Incidente

Ao detectar exposição: interromper o fluxo, preservar evidências mínimas, revogar segredo
se houver, identificar alcance, avisar o responsável apropriado, corrigir causa e registrar
decisão. Não copiar o conteúdo exposto para o relatório do incidente.

## 12. Checklist por gate

- classe definida;
- finalidade e mínimo necessários;
- fonte/vigência conferidas;
- acesso local/externo permitido;
- teste negativo de vazamento;
- logs revisados;
- retenção definida;
- pessoa responsável identificada;
- pendência registrada quando faltar autorização.
