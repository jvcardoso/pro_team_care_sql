# Estratégia de Testes - Pro Team Care

## 1. Objetivo

Este documento define a estratégia e os requisitos mínimos de testes para qualquer alteração ou nova funcionalidade no projeto Pro Team Care. O objetivo é garantir a qualidade, prevenir regressões (bugs que retornam) e manter o sistema estável à medida que ele evolui.

O princípio que guia esta estratégia é a **Pirâmide de Testes**.

## 2. Estrutura de Diretórios de Testes

Para manter a organização, todos os testes devem seguir a seguinte estrutura:

- `backend/tests/unit/`: Testes de unidade para o backend (lógica de negócio isolada).
- `backend/tests/integration/`: Testes de integração para o backend (principalmente testes de API).
- `frontend/tests/unit/`: Testes de unidade para componentes React isolados.
- `frontend/tests/integration/`: Testes de integração para hooks ou serviços que interagem com APIs (usando mocks).
- `frontend/e2e/`: Testes de ponta a ponta (E2E) que simulam o usuário no navegador (Playwright).

## 3. O Contrato de Testes (Requisitos Mínimos por Mudança)

Toda nova alteração no código deve ser acompanhada de testes, conforme os cenários abaixo.

--- 

### Cenário 1: Criação de um Novo Endpoint no Backend

**Exemplo:** `POST /api/v1/patients`

**Requisito Mínimo:**
- **1 Teste de Integração (`pytest`)** contendo no mínimo:
    1.  **Teste de Sucesso (Caminho Feliz):** Uma chamada à API com dados válidos, verificando se a resposta é `201 Created` e se os dados foram salvos corretamente no banco de dados de teste.
    2.  **Teste de Validação (Caminho Triste):** Uma chamada com dados inválidos (ex: campo obrigatório faltando), verificando se a resposta é `422 Unprocessable Entity`.
    3.  **Teste de Autorização:** Uma chamada sem um token de autenticação válido, verificando se a resposta é `401 Unauthorized`.

**Recomendado:**
- Se o endpoint contiver uma lógica de negócio complexa (ex: um cálculo específico), essa lógica deve ser extraída para uma função em um `service` e ter seu próprio **Teste de Unidade**.

--- 

### Cenário 2: Criação de uma Nova Página com Formulário no Frontend

**Exemplo:** Página de cadastro de pacientes.

**Requisito Mínimo:**
- **1 Teste de Integração (`Jest` + `Testing Library`)** que:
    1.  Renderiza a página.
    2.  Simula o usuário preenchendo os campos do formulário.
    3.  Simula o clique no botão "Salvar".
    4.  Verifica se a função do `service` que chama a API foi acionada com os dados corretos do formulário. (A chamada à API real deve ser "mockada"/simulada para não depender do backend).

**Recomendado:**
- Se o formulário usar componentes complexos e reutilizáveis (ex: um seletor de datas especial), estes componentes devem ter seus próprios **Testes de Unidade**.

--- 

### Cenário 3: Correção de um Bug (Backend ou Frontend)

**Requisito Mínimo:**
1.  **Escrever um novo teste (de unidade ou integração) que reproduza o bug.** Este teste deve falhar antes da sua correção.
2.  Aplicar a correção no código da aplicação.
3.  Rodar o novo teste e confirmar que ele agora passa. 

Isso é chamado de **Teste de Regressão** e garante que o bug nunca mais voltará a acontecer sem que a equipe seja notificada pela falha do teste.

--- 

## 4. Como Estruturar o que Já Existe (Legado)

Não é prático parar para testar todo o sistema de uma vez. A abordagem será gradual e focada em risco:

1.  **Prioridade 1 - APIs Críticas:** Começar escrevendo **Testes de Integração (`pytest`)** para os endpoints mais importantes do sistema que ainda não têm testes (ex: Login, CRUD de Empresas, CRUD de Usuários).

2.  **Prioridade 2 - Regra do Escoteiro:** Ao corrigir um bug ou fazer uma pequena alteração em uma parte do código que **não tem testes**, aproveite a oportunidade para adicionar pelo menos um teste que cubra a sua mudança (seguindo o Cenário 3). *"Deixe a área de acampamento mais limpa do que você a encontrou."*

3.  **Prioridade 3 - Fluxos Críticos E2E:** Identificar os 3 a 5 fluxos de usuário mais críticos para o negócio (ex: Login completo, Cadastro de uma empresa do início ao fim) e criar um **Teste E2E (`Playwright`)** para cada um.
