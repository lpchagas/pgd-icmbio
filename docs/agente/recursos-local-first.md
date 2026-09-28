# AT-02 — Recursos disponíveis e arquitetura local-first

**Versão:** 1.0  
**Data de verificação:** 23.08.2026  
**Decisão relacionada:** [ADR-008](../decisoes/ADR-008-desenvolvimento-individual-local-first.md)  
**Situação:** análise técnica vigente para o protótipo individual

## 1. Conclusão

É possível desenvolver e demonstrar o agente sem cobrança incremental obrigatória usando
o computador local, MySQL, FastAPI, bibliotecas abertas e as ferramentas de
desenvolvimento já disponíveis ao desenvolvedor, sem custo institucional. Essas
ferramentas apoiam o desenvolvimento, mas não constituem licenciamento de backend ou
publicação institucional.

GPTs personalizados não resolvem o caso atual: segundo a documentação consultada, planos
individuais do ChatGPT não podem criar ou publicar novos GPTs; criação é restrita a
workspaces Business, Enterprise e Edu elegíveis. Além disso, um GPT não substituiria o
motor local, o banco versionado e os controles de dados. [OpenAI — Creating and editing
GPTs](https://help.openai.com/en/articles/8554397-creating-a-gpt).

## 2. Inventário confirmado

| Recurso | Situação observada | Uso recomendado | Limitação determinante |
| --- | --- | --- | --- |
| Assistentes de programação com IA (Codex, Claude Code e similares) | planos individuais do desenvolvedor, sem custo institucional | escrever, revisar e testar código; pesquisa e documentação | planos individuais não incluem API nem licença institucional |
| Microsoft 365 | licença institucional | Office, identidade e colaboração | não equivale a capacidade Copilot Studio |
| Power Apps, Copilot Studio, Fabric e Power Automate | licenças individuais, gratuitas ou de avaliação | experimento de interface e exploração | não autorizam publicação institucional nem servem de base duradoura |

## 3. OpenAI

O Codex está incluído nos planos ChatGPT, com limites variáveis por plano, e é adequado
para escrever, revisar e testar código. O conteúdo processado em planos individuais segue os
controles da conta do usuário; conversas podem ser usadas para melhoria se o usuário não
desativar o treinamento. Conteúdo institucional deve, portanto, respeitar a classificação
e preferir o fluxo local. [OpenAI — Using Codex with your ChatGPT
plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan).

ChatGPT e API usam sistemas de cobrança separados. A proposta não deve considerar a
assinatura do ChatGPT como crédito de API. [OpenAI — ChatGPT versus API
billing](https://help.openai.com/en/articles/9039756-billing-settings-in-chatgpt-vs-platform).

**Decisão:** usar o Codex como ferramenta de desenvolvimento; não usar GPT
personalizado ou OpenAI API como dependência do protótipo.

## 4. Anthropic

Planos individuais do Claude podem apoiar revisão e o Claude Code no limite do plano, mas o
consumo de API é separado. Fontes: [planos individuais do Claude](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan)
e [Claude Code com Pro/Max](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan).

**Decisão:** usar para desenvolvimento e verificação cruzada; não tratar como backend.

## 5. Google

A Gemini Developer API oferece combinações de nível gratuito e pago que variam por modelo,
limite e uso de dados. As condições devem ser verificadas antes de cada ativação.
[Google — Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

**Decisão:** nível gratuito é opcional e recebe somente dados públicos ou sintéticos. O
protótipo deve continuar operável sem ele.

## 6. Microsoft

Power Apps Premium é útil para uma prova individual, mas a distribuição depende do modo de
licenciamento, aplicativo e usuários. [Microsoft — Power Apps licensing
FAQ](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-licensing-faq).

O trial viral do Copilot Studio pode permitir criação exploratória, mas licenças trial
podem impedir acesso ou publicação e não substituem uma licença adequada do tenant.
[Microsoft — Copilot Studio license and publish
errors](https://learn.microsoft.com/en-us/troubleshoot/power-platform/copilot-studio/licensing/publish-license-error).

**Decisão:** FastAPI `/docs` é a interface-base; Power Apps é spike opcional; Copilot
Studio é destino institucional futuro, condicionado a workspace/licença/administração.

## 7. Complementos gratuitos

| Serviço | Oportunidade | Uso permitido | Risco/controle |
| --- | --- | --- | --- |
| GitHub Actions | lint, links e testes em repositório público | documentação e dados sintéticos | limites/cobrança variam; conferir antes de privado |
| Cloudflare Quick Tunnel | demonstração temporária sem conta | API com dados sintéticos | sem SLA; não produção nem conteúdo institucional |
| bibliotecas Python abertas | FastAPI, Pydantic, PyMySQL, testes e RAG | ambiente local | fixar versões e auditar dependências |
| modelos locais | processar conteúdo institucional comum | computador autorizado | desempenho/qualidade e licença do modelo |

GitHub informa que runners padrão em repositórios públicos são gratuitos; repositórios
privados usam franquia e cobrança conforme plano. [GitHub Actions
billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

Cloudflare descreve Quick Tunnels como recurso de teste, sem SLA, com limites e sem suporte
para produção. [Cloudflare Quick
Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/).

## 8. Arquitetura recomendada

| Camada | Escolha-base | Custo incremental | Dados permitidos |
| --- | --- | ---: | --- |
| Interface | FastAPI `/docs` local | zero | conforme acesso local |
| API/motor | Python, FastAPI e Pydantic | zero | institucional permitido |
| Banco | MySQL 8 local | zero | modelo mínimo governado |
| RAG | indexação e modelo local | zero | público e institucional comum autorizado |
| Indicadores | Denodo JDBC leitura | existente | consulta institucional autorizada |
| Desenvolvimento | assistentes de programação (Codex, Claude Code) | zero institucional | código e documentação; dados só públicos ou sintéticos |
| IA externa opcional | Gemini free tier | zero condicionado | público/sintético |
| Demonstração externa | Quick Tunnel | zero condicionado | exclusivamente sintético |

## 9. Decisões de não dependência

- não depender de GPT personalizado;
- não depender de OpenAI/Anthropic API paga;
- não depender de trial viral do Copilot Studio;
- não depender de Fabric ou Power Automate para o núcleo;
- não depender de túnel gratuito para operação;
- não enviar corpus institucional a tier gratuito externo.

## 10. Reavaliação

Rever este AT antes de publicar para terceiros, iniciar piloto, mudar política de dados,
ativar API externa ou após seis meses. Registrar data, fonte oficial e decisão resultante.
