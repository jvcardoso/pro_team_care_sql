# Análise de Viabilidade - Módulo de Gestão de Atividades com IA

**Data:** 2025-11-03 14:30
**Versão:** v001
**Autor:** Gemini
**Revisão de:** N/A
**Motivo da revisão:** N/A

## Histórico de Versões
- v001 (2025-11-03): Criação do documento inicial para análise de viabilidade da nova funcionalidade.

## Objetivo
Analisar a viabilidade e o escopo da criação de um novo módulo de sistema, focado em produtividade pessoal e geração de relatórios gerenciais. O módulo permitirá ao usuário registrar atividades colando textos ou imagens (prints), com uma IA auxiliando na extração de dados e classificação, e posterior geração de relatórios no estilo ITIL.

## Metodologia
Para esta análise conceitual, os métodos de investigação foram adaptados da seguinte forma:

- **Systematic Investigation (Investigação Sistemática):** Decompor a ideia em seus principais componentes funcionais: Interface do Usuário (UI), Processamento de IA, Armazenamento de Dados e Geração de Relatórios.
- **5 Whys Method (Método dos 5 Porquês):** Questionar a necessidade de cada componente para destilar o valor central da proposta e identificar os requisitos fundamentais.
- **Differential Analysis (Análise Diferencial):** Comparar a abordagem "com IA" versus uma abordagem puramente "manual" para avaliar ganhos de produtividade, complexidade e custo.
- **Forensic Analysis (Análise Forense de Código):** Analisar a estrutura atual do projeto (FastAPI + React) para determinar o melhor caminho de integração do novo módulo sem impactar a arquitetura existente.
- **Deep Debugging (Debug Aprofundado):** Aplicado de forma teórica para antecipar os principais desafios técnicos, riscos e "bugs" conceituais na ideia.

## Resultados

### 1. Decomposição da Funcionalidade

O módulo pode ser dividido em quatro áreas principais:

- **Frontend (Painel de Registro):**
  - Uma interface semelhante a um chat (ex: Gemini, Perplexity).
  - Área para colar texto ou fazer upload/colar imagens (prints).
  - Campos para o usuário complementar/corrigir os dados extraídos pela IA, como:
    - Título/Assunto da Atividade
    - Data de Ocorrência / Prazo
    - Pessoas/Sistemas Envolvidos
    - Status (Pendente, Em Andamento, Concluído, Cancelado)
    - Tags/Categorias (para alinhamento com ITIL, ex: "Gestão de Incidentes", "Requisição de Serviço").

- **Backend (API e Lógica de Negócio):**
  - Endpoints para receber o conteúdo (texto/imagem) e os dados do formulário.
  - Orquestração da chamada para o serviço de IA.
  - Lógica para salvar a atividade e seus metadados no banco de dados.
  - Endpoints para consulta das atividades (com filtros por data, status, etc.).
  - Endpoint para geração dos relatórios consolidados.

- **Inteligência Artificial (Componente de Extração):**
  - **Input:** Texto ou imagem.
  - **Processamento:** Um modelo de linguagem (LLM), possivelmente com capacidade de visão (multimodal), analisaria o conteúdo para extrair:
    - **Entidades:** Nomes de pessoas, empresas, sistemas.
    - **Datas e Prazos:** "amanhã", "próxima sexta", "15/12/2025".
    - **Contexto/Sentimento:** Tenta inferir o assunto principal e a urgência.
  - **Output:** Um objeto JSON estruturado com os dados extraídos, para pré-preenchimento do formulário no frontend.
  - **Tecnologia:** Requer a integração com uma API de IA externa (ex: Google AI Platform, OpenAI, etc.).

- **Banco de Dados (Armazenamento):**
 
  - Novas tabelas para armazenar as atividades, por exemplo: `[core].activities`, `[core].activity_responsibles`, `[core].activity_tags`.
  - As tabelas devem incluir `company_id` e `user_id` para garantir o isolamento de dados (multi-tenant).

### 2. Análise de Viabilidade

- **Conceito:** A ideia é **altamente viável e relevante**. Ela ataca um problema real de gestão de tempo e formalização de demandas informais (e-mails, chats). A capacidade de gerar relatórios estruturados a partir de dados não-estruturados é um grande diferencial. Não é um conceito ruim, pelo contrário, é inovador.

- **Técnica (Stack Atual):** A arquitetura FastAPI + React é perfeitamente adequada para construir os componentes de Frontend e Backend. A integração com uma API de IA é uma tarefa comum e bem documentada.

- **Riscos e Desafios:**
  1. **Assertividade da IA:** A extração de dados não será 100% perfeita. O usuário **sempre** precisará revisar e corrigir os dados. A UX deve ser projetada com isso em mente, tornando a correção fácil e rápida.
  2. **Custo:** APIs de IA generativa (especialmente com visão) têm um custo por chamada. O uso intensivo pode gerar uma despesa operacional significativa.
  3. **Complexidade dos Relatórios ITIL:** Gerar relatórios que façam sentido dentro de um framework como ITIL exige uma categorização (tagging) muito disciplinada por parte do usuário. A IA pode sugerir tags, mas a consistência dependerá do usuário.
  4. **Processamento de Imagens (OCR):** A extração de texto de imagens (OCR) é mais complexa e propensa a erros do que a análise de texto puro.

## Conclusões
O conceito é **excelente e viável**, com grande potencial de agregar valor. Ele transforma tarefas diárias não-estruturadas em dados metrificáveis, o que é o sonho de qualquer gestor focado em processos.

A chave para o sucesso não é a perfeição da IA, mas sim a **fluidez da interação homem-máquina**. A IA atua como um "assistente" que acelera o preenchimento, e o usuário finaliza e valida.

A melhor forma de abordar seria através de um **MVP (Produto Mínimo Viável)**, para validar o fluxo principal e o valor percebido antes de construir todas as funcionalidades de relatório.

## Próximos passos
Para refinar o entendimento e planejar um MVP, sugiro que você responda às seguintes questões. Suas respostas nos ajudarão a definir o escopo inicial.

1.  **Prioridade de Extração:** Dos dados a serem extraídos pela IA (responsáveis, datas, assunto), qual é o **mais importante** para começar? Podemos focar em apenas um ou dois no início para simplificar.

2.  **Modelo de Relatório:** Você poderia fornecer um exemplo simples de um relatório diário ou semanal que você gostaria de ver? (Ex: uma tabela com colunas: Data, Assunto, Responsável, Status). Isso nos ajudaria a modelar os dados corretamente.

3.  **Fonte dos Dados:** Inicialmente, o sistema dependerá apenas de conteúdo que você **cola manualmente**? Ou você vislumbra integrações diretas (ex: um plugin de Outlook ou Teams) no futuro?

4.  **MVP Manual vs. IA:** Você estaria disposto a começar com uma versão **totalmente manual** (você preenche todos os campos, sem ajuda da IA) para validar a utilidade do registro e dos relatórios? Isso reduziria drasticamente a complexidade e o custo inicial. A IA poderia ser adicionada na fase 2.
