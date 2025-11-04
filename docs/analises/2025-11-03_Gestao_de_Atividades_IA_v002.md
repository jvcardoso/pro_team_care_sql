# Análise de Viabilidade - Módulo de Gestão de Atividades com IA

**Data:** 2025-11-03 15:00
**Versão:** v002
**Autor:** Gemini
**Revisão de:** v001
**Motivo da revisão:** Adicionar profundidade estratégica, incluindo campos obrigatórios, melhoria de prompt para IA, estrutura de dados para base de conhecimento e um novo "Board de Pendências".

## Histórico de Versões
- v002 (2025-11-03): Expansão do conceito para incluir base de conhecimento e gestão de pendências.
- v001 (2025-11-03): Criação do documento inicial para análise de viabilidade.

## Objetivo
Analisar a viabilidade de um módulo de produtividade que, além de registrar atividades via texto/imagem, utiliza metadados fornecidos pelo usuário para aprimorar a análise da IA. O sistema deve estruturar os dados para servirem como uma **base de conhecimento** e incluir um **board de gestão de pendências** para acompanhamento de impeditivos e entregas.

## Metodologia
A mesma da v001, com foco adicional na modelagem de dados e na arquitetura de fluxo de informações entre o usuário, o sistema e a IA.

## Resultados

### 1. Decomposição da Funcionalidade (Revisado)

O módulo agora é visto como um ecossistema com cinco áreas:

- **Frontend (Painel de Registro):**
  - Interface de registro rápido (texto/imagem).
  - **Campos Obrigatórios:** Para garantir o contexto mínimo para a IA e para a base de conhecimento. Sugestão:
    - **Título/Assunto da Atividade (Obrigatório):** Define o objetivo principal.
    - **Status (Obrigatório):** (Pendente, Em Andamento, Concluído, Cancelado).
  - **Campos Opcionais (Pré-preenchidos pela IA):**
    - Data de Ocorrência / Prazo
    - Pessoas/Sistemas Envolvidos
    - Tags/Categorias (ex: "Gestão de Incidentes", "Requisição de Serviço").

- **Backend (API e Lógica de Negócio Revisada):**
  - **Engenharia de Prompt Dinâmica:** A API irá construir um prompt otimizado para a IA, combinando o conteúdo bruto (texto/imagem) com os metadados estruturados dos campos obrigatórios.
    - *Exemplo de Prompt:* "Analise o seguinte conteúdo no contexto de '{Título da Atividade}'. O status atual é '{Status}'. Extraia as pessoas envolvidas, prazos e sugira tags relevantes para uma base de conhecimento de TI."
  - Orquestração da chamada para o serviço de IA.
  - Lógica para salvar a atividade, seus metadados, o input bruto, e o output da IA.
  - Endpoints para o novo Board de Pendências.

- **Inteligência Artificial (Componente de Extração e Análise):**
  - **Função Primária Revisada:**
    1.  **Análise Contextual:** Entender o conteúdo com base no prompt enriquecido.
    2.  **Sugestão de Tags:** Identificar e sugerir categorias para a base de conhecimento.
    3.  **Identificação de Pendências:** Sinalizar possíveis ações, prazos ou itens que necessitam de acompanhamento.
    4.  **Geração de Alertas:** Identificar urgência ou riscos e sugerir a criação de um card de alerta no board.

- **Banco de Dados (Estrutura para Base de Conhecimento):**
  - A modelagem deve ser mais robusta para permitir análises futuras e reprocessamento.
  - **Tabela Principal: `[core].Activities`**
    - `ActivityID`, `UserID`, `CompanyID`, `Title`, `Status`, `CreationDate`, `DueDate`.
  - **Tabela de Conteúdo: `[core].ActivityContents`**
    - `ContentID`, `ActivityID`, `RawText` (o texto colado), `RawImage` (path para a imagem), `AIExtractionJSON` (o JSON bruto retornado pela IA), `UserCorrectedJSON` (os dados finais validados pelo usuário).
    - *Justificativa:* Salvar os dados em estágios permite auditar, treinar futuros modelos e entender onde a IA falha.
  - **Tabela de Entidades: `[core].ActivityEntities`**
    - `EntityID`, `ActivityID`, `EntityType` (Pessoa, Sistema), `EntityName`.
  - **Tabela de Pendências: `[core].Pendencies`**
    - `PendencyID`, `ActivityID`, `Description`, `Owner` (quem deve agir), `Status` (Pendente, Cobrado, Resolvido), `Impediment` (texto descrevendo o bloqueio).

- **(NOVO) Frontend (Board de Pendências):**
  - Uma visualização em estilo Kanban (ex: Trello, Jira).
  - Colunas como "Pendentes", "Aguardando Terceiros", "Impedimentos", "Concluídas".
  - Cards representando as pendências extraídas das atividades.
  - Cada card deve ser clicável, levando de volta à atividade de origem.
  - Filtros por pessoa responsável, prazo, etc.

### 2. Análise de Viabilidade (Revisada)

- **Conceito:** A sofisticação do conceito aumenta seu valor exponencialmente. Ele evolui de um simples "bloco de notas inteligente" para uma **ferramenta de gestão de conhecimento e produtividade pessoal (PKM - Personal Knowledge Management)**.
- **Riscos e Desafios:**
  - **Complexidade da UI/UX:** A interface precisa ser muito bem desenhada para não sobrecarregar o usuário com tantos campos e opções, mantendo a agilidade do registro.
  - **Complexidade do Backend:** A lógica de negócio se torna mais complexa, especialmente na gestão do ciclo de vida das pendências e na correlação dos dados.

## Conclusões (Revisada)
A proposta revisada é **estrategicamente superior**. A obrigatoriedade de campos e o enriquecimento do prompt transformam a IA de uma ferramenta "mágica" e pouco confiável em um assistente poderoso e contextualizado. A criação de uma base de conhecimento e de um board de pendências ataca diretamente as dores de organização, rastreabilidade e acompanhamento de tarefas.

O MVP (Produto Mínimo Viável) agora poderia ser focado no fluxo de **registro com campos obrigatórios e a criação manual de um card de pendência**, validando o core da gestão de tarefas antes de automatizar a extração com IA.

## Próximos passos (Revisados)
As perguntas foram atualizadas para refletir o novo escopo:

1.  **Campos Obrigatórios:** Para o MVP, quais seriam os campos **absolutamente essenciais** que você preencheria para criar uma atividade e uma pendência? (Ex: Título, Status da Atividade, Descrição da Pendência, Responsável pela Pendência).

2.  **Board de Pendências:** Quais são as colunas/status mais importantes para o seu fluxo de trabalho no board de pendências? (Ex: "Para Fazer", "Em Andamento", "Aguardando Resposta", "Feito").

3.  **Base de Conhecimento:** Pensando no futuro, que tipo de pergunta você gostaria de fazer à sua base de conhecimento? (Ex: "Quais atividades relacionadas ao 'Sistema X' tiveram o status 'Impedimento' nos últimos 3 meses?").

4.  **Prioridade de Features:** Entre a **extração automática da IA** e o **Board de Pendências funcional**, qual das duas funcionalidades traria mais valor para você no primeiro momento?