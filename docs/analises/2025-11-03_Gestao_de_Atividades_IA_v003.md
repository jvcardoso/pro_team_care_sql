# Análise e Plano de Implementação - Módulo de Gestão de Atividades com IA

**Data:** 2025-11-03 15:45
**Versão:** v003
**Autor:** Gemini
**Revisão de:** v002
**Motivo da revisão:** Consolidar todas as discussões, adicionar um exemplo prático de uso e detalhar um plano de implementação para o MVP.

## Histórico de Versões
- v003 (2025-11-03): Adição do plano de implementação do MVP e consolidação final.
- v002 (2025-11-03): Expansão do conceito para incluir base de conhecimento e gestão de pendências.
- v001 (2025-11-03): Criação do documento inicial para análise de viabilidade.

## 1. Objetivo
Analisar e detalhar o plano de implementação de um módulo de produtividade e gestão de conhecimento. O sistema permitirá o registro de atividades, usará IA como assistente de extração de dados, e fornecerá um board de pendências para acompanhamento de tarefas, com todos os dados servindo como uma base de conhecimento pesquisável.

## 2. Arquitetura e Funcionalidades

### 2.1. Fluxo de Trabalho (Usuário -> IA -> Banco de Dados)
O princípio central é que o usuário está sempre no controle. A IA é um assistente.

1.  **Entrada de Dados:** O usuário insere o conteúdo bruto (texto/imagem) e preenche campos obrigatórios (ex: Título, Status).
2.  **Análise da IA:** O sistema envia os dados para uma IA, que sugere preenchimentos para campos como Pessoas Envolvidas, Tags e Pendências.
3.  **Tela de Validação:** A interface é pré-preenchida com as sugestões da IA. O usuário tem total liberdade para corrigir, adicionar ou remover informações.
4.  **Gravação:** Somente após o usuário clicar em "Salvar", os dados finais e validados são persistidos no banco de dados.

### 2.2. Componentes do Sistema
- **Frontend:** Painel de registro, tela de validação e board de pendências em estilo Kanban.
- **Backend:** API para orquestrar a lógica, engenharia de prompt dinâmica para a IA e endpoints para o CRUD de atividades/pendências.
- **Inteligência Artificial:** Serviço externo para análise contextual, sugestão de tags e identificação de pendências.
- **Banco de Dados:** Modelagem robusta para suportar a funcionalidade de base de conhecimento.

### 2.3. Estrutura do Banco de Dados
- **`[core].Activities`**: Armazena o registro principal da atividade.
- **`[core].ActivityContents`**: Armazena o conteúdo bruto, a extração da IA e os dados validados pelo usuário.
- **`[core].ActivityEntities`**: Relaciona entidades (pessoas, sistemas, links) a uma atividade.
- **`[core].Pendencies`**: Tabela dedicada para as pendências, com descrição, responsável e status.

### 2.4. Exemplo Prático de Uso (Simulação de Mesa)
(Esta seção formaliza a simulação que realizamos anteriormente)

- **Input:** Um chat sobre a RDM CHG0076721.
- **Ações do Sistema:**
    1.  **Análise:** A IA, com o contexto do título "Abertura RDM...", analisa o chat.
    2.  **Sugestão:** Sugere as pessoas "Vania", "Daniel", etc., e identifica duas pendências claras: a necessidade do "de acordo" e a obtenção dos testes.
    3.  **Validação:** O usuário confirma as sugestões.
    4.  **Resultado:** A atividade é salva, e dois cards são criados automaticamente no board de pendências, um para cada impedimento, atribuídos aos respectivos responsáveis.

## 3. Plano de Implementação Sugerido (MVP)
Propomos uma abordagem faseada para entregar valor rapidamente e validar as funcionalidades principais.

### Fase 1: O Esqueleto Funcional (Backend e Banco de Dados)
O objetivo é criar a fundação do sistema, sem nenhuma interface de usuário ainda.

- **Tarefa 1.1 (Banco de Dados):** Criar o script SQL `042_Create_Activity_Tracker_Tables.sql` no diretório `Database/` com as tabelas `Activities`, `ActivityContents`, `ActivityEntities` e `Pendencies`.
- **Tarefa 1.2 (Backend):** Criar os modelos SQLAlchemy correspondentes em `backend/app/models/`.
- **Tarefa 1.3 (Backend):** Criar os schemas Pydantic (Create, Update, Response) em `backend/app/schemas/`.
- **Tarefa 1.4 (Backend):** Implementar o `Repository` e o `Service` para o CRUD básico das novas tabelas, seguindo o padrão já existente no projeto.
- **Tarefa 1.5 (Backend):** Criar os endpoints da API em `backend/app/api/v1/` para:
    - `POST /activities` (cria uma nova atividade)
    - `GET /activities` (lista atividades)
    - `POST /pendencies` (cria uma pendência associada a uma atividade)
    - `GET /pendencies` (lista pendências, com filtros)

### Fase 2: A Interface Mínima (Frontend Manual)
O objetivo é ter um sistema 100% funcional para registro e acompanhamento manual, validando o core da proposta de valor.

- **Tarefa 2.1 (Frontend):** Criar uma nova página/rota em React, por exemplo, `/atividades`.
- **Tarefa 2.2 (Frontend):** Desenvolver um formulário de registro que interage com o endpoint `POST /activities`, permitindo o cadastro **manual** de uma atividade e suas pendências.
- **Tarefa 2.3 (Frontend):** Desenvolver o componente "Board de Pendências", que consome o endpoint `GET /pendencies` e exibe os cards em colunas (ex: "Pendente", "Em Andamento", "Concluído").

### Fase 3: A Inteligência (Integração com IA)
Com o sistema manual validado, adicionamos a camada de inteligência.

- **Tarefa 3.1 (Backend):** Adicionar a chave da API de IA no arquivo `.env` e criar um serviço cliente para se comunicar com ela.
- **Tarefa 3.2 (Backend):** Modificar o endpoint `POST /activities` para receber o texto bruto, chamar o serviço da IA e retornar suas sugestões junto com a resposta.
- **Tarefa 3.3 (Frontend):** Modificar o formulário de registro para suportar a análise da IA, pré-preenchendo os campos e implementando a "Tela de Validação".

### Fase 4: Relatórios e Melhorias
- Implementar endpoints e interfaces para geração de relatórios.
- Adicionar filtros avançados, buscas na base de conhecimento e notificações.