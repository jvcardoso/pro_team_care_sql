# 🎯 PLANO DE TESTES E VALIDAÇÕES - CRUD EMPRESAS

**Data:** 28/10/2025  
**Objetivo:** Plano abrangente de testes das APIs CRUD de empresa, replicando o fluxo completo do frontend  
**Baseado em:** TESTING_STRATEGY.md, fluxos E2E existentes e documentação de APIs

---

## 📊 CONTEXTO

### Fluxo do Frontend Identificado
Baseado na análise dos testes E2E (`company-registration.spec.ts`):

1. **Login** → Autenticação JWT
2. **Navegação** → `/admin/empresas?view=create`
3. **Consulta CNPJ** → Busca dados na Receita Federal
4. **Preenchimento** → Razão Social, Nome Fantasia, Telefones, Emails, Endereços
5. **Validações** → CNPJ duplicado, campos obrigatórios, formato CEP
6. **Submissão** → Criação completa via stored procedure
7. **Redirecionamento** → Lista ou detalhes da empresa criada

### APIs CRUD Identificadas
| Operação | Endpoint | Status | Testes Existentes |
|----------|----------|--------|-------------------|
| **Criação** | `POST /api/v1/companies/complete` | ✅ Funcional | `test_company_complete.py` |
| **Listagem** | `GET /api/v1/companies/complete-list` | ✅ Funcional | Parcial |
| **Detalhes** | `GET /api/v1/companies/{id}` | ✅ Funcional | - |
| **Atualização** | `PUT /api/v1/companies/{id}/complete` | ⚠️ Pendente | - |
| **Exclusão** | `DELETE /api/v1/companies/{id}` | ✅ Funcional | - |
| **Busca CNPJ** | `GET /api/v1/companies/cnpj/{cnpj}` | ✅ Funcional | - |
| **Validação CNPJ** | `GET /api/v1/companies/validate/cnpj/{cnpj}` | ✅ Funcional | - |
| **Contatos** | `GET /api/v1/companies/{id}/contacts` | ✅ Funcional | - |
| **Audit Log** | `GET /api/v1/lgpd/companies/{id}/audit-log` | ✅ Funcional | `test_audit_logs.py` |
| **Reveal Campo** | `POST /api/v1/lgpd/companies/{id}/reveal-field` | ✅ Funcional | `test_lgpd.py` |

---

## 🧪 ESTRATÉGIA DE TESTES

Seguindo a **Pirâmide de Testes** definida em `TESTING_STRATEGY.md`:

### 1. Testes de Unidade (Backend)
- **Cobertura:** Lógica isolada, validações, utilitários
- **Framework:** `pytest` com mocks
- **Localização:** `backend/tests/unit/`

### 2. Testes de Integração (Backend)
- **Cobertura:** APIs completas, banco de dados, stored procedures
- **Framework:** `pytest` + `httpx`
- **Localização:** `backend/tests/integration/`

### 3. Testes E2E (Frontend)
- **Cobertura:** Fluxo completo usuário, replicando uso real
- **Framework:** Playwright
- **Localização:** `frontend/e2e/`

---

## 📋 PLANO DETALHADO POR API

### 🔐 1. AUTENTICAÇÃO (Pré-requisito)
**Endpoint:** `POST /api/v1/auth/login`

#### Testes de Integração (Backend)
- ✅ **Login sucesso** - Credenciais válidas → 200 + token JWT
- ✅ **Login falha** - Senha incorreta → 401 + log no banco
- ✅ **Login usuário inativo** - Conta desativada → 401 + log
- ✅ **Login email inexistente** - Email não cadastrado → 401 + log

#### Testes E2E (Frontend)
- ✅ **Fluxo login completo** - Form → API → Redirecionamento

---

### 🌐 2. SERVIÇOS EXTERNOS DE APOIO AO CADASTRO
**Funcionalidades:** Consulta CEP, Receita Federal, Geocoding

#### 📍 2.1 Consulta CEP (ViaCEP)
**Serviço:** ViaCEP API (`https://viacep.com.br/ws/{cep}/json/`)

##### Cenário: CEP Válido
**Testes de Integração:**
```python
# backend/tests/integration/test_external_services.py
async def test_consultar_cep_valido():
    # Arrange: CEP válido
    cep = "01001000"

    # Act: Consultar ViaCEP
    response = await address_service.consult_viacep(cep)

    # Assert: Dados retornados
    assert response is not None
    assert "logradouro" in response
    assert "bairro" in response
    assert "localidade" in response
    assert "uf" in response
```

##### Cenário: CEP Inválido
```python
async def test_consultar_cep_invalido():
    # Arrange: CEP inexistente
    cep = "99999999"

    # Act: Consultar ViaCEP
    response = await address_service.consult_viacep(cep)

    # Assert: None retornado
    assert response is None
```

#### 🏢 2.2 Consulta Receita Federal (CNPJ)
**Serviço:** ReceitaWS API (`https://receitaws.com.br/v1/cnpj/{cnpj}`)

##### Cenário: CNPJ Válido
```python
async def test_consultar_cnpj_receita_valido():
    # Arrange: CNPJ válido
    cnpj = "11222333000144"

    # Act: Consultar Receita Federal
    response = await cnpj_service.consultar_receita(cnpj)

    # Assert: Dados da empresa retornados
    assert response.success is True
    assert "nome" in response.data
    assert "fantasia" in response.data
    assert "logradouro" in response.data
```

##### Cenário: CNPJ Inválido
```python
async def test_consultar_cnpj_receita_invalido():
    # Arrange: CNPJ inexistente
    cnpj = "99999999000199"

    # Act: Consultar Receita Federal
    response = await cnpj_service.consultar_receita(cnpj)

    # Assert: Erro retornado
    assert response.success is False
    assert "não encontrado" in response.message.lower()
```

#### 🗺️ 2.3 Geocoding de Endereços
**Serviço:** Nominatim OpenStreetMap

##### Cenário: Endereço Completo
```python
async def test_geocoding_endereco_completo():
    # Arrange: Endereço completo
    endereco = "Rua das Flores, 123, Centro, São Paulo, SP"

    # Act: Geocoding
    response = await geocoding_service.geocode_address(endereco)

    # Assert: Coordenadas retornadas
    assert response is not None
    assert "latitude" in response
    assert "longitude" in response
    assert response["latitude"] != 0
    assert response["longitude"] != 0
```

---

### 📝 3. CRIAÇÃO DE EMPRESA (INTEGRANDO SERVIÇOS EXTERNOS)
**Endpoint:** `POST /api/v1/companies/complete`

#### Cenário: Cadastro Completo com Enriquecimento Automático
**Fluxo:** CNPJ → Receita Federal → CEP → ViaCEP → Geocoding → Submissão

**Testes de Integração (Backend):**
```python
# backend/tests/integration/test_company_complete_with_external.py
async def test_criar_empresa_com_enriquecimento_externo():
    # Arrange: Dados básicos + CEP para enriquecimento
    company_data = {
        "pj_profile": {
            "name": "Empresa Teste Ltda",
            "tax_id": "11222333000144",  # CNPJ que existe na Receita
            "trade_name": "Empresa Teste"
        },
        "addresses": [{
            "zip_code": "01001000",  # CEP válido para ViaCEP
            "number": "123",
            "is_principal": True
        }],
        "phones": [{"number": "11999999999", "is_principal": True}],
        "emails": [{"email_address": "contato@empresa.com", "is_principal": True}]
    }

    # Act: POST /api/v1/companies/complete
    response = await client.post("/api/v1/companies/complete", json=company_data)

    # Assert: 201 + enriquecimento automático
    assert response.status_code == 201
    data = response.json()

    # Verificar que dados foram enriquecidos automaticamente
    # PJ Profile enriquecido com Receita Federal
    # Address enriquecido com ViaCEP
    # Coordenadas adicionadas via Geocoding
```

**Testes E2E (Frontend) - Fluxo Completo com APIs Externas:**
```typescript
// frontend/e2e/company-registration-with-external-apis.spec.ts
test("cadastro empresa com enriquecimento automático", async ({ page }) => {
    // 1. Login e navegação
    await page.goto("/login");
    // ... login steps ...

    // 2. Navegar para formulário de empresa
    await page.goto("/admin/empresas?view=create");

    // 3. Preencher CNPJ e consultar Receita Federal
    const cnpjInput = page.getByLabel("CNPJ");
    await cnpjInput.fill("05.514.464/0001-30"); // CNPJ real

    const consultarBtn = page.getByRole("button", { name: /consultar/i });
    await consultarBtn.click();

    // 4. Verificar auto-preenchimento Receita Federal
    await expect(page.getByLabel("Razão Social")).toHaveValue("BRAZIL HOME CARE...");
    await expect(page.getByLabel("Nome Fantasia")).toHaveValue("DOMICILE HOME CARE");

    // 5. Preencher CEP e verificar ViaCEP
    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill("13201840"); // CEP real

    // Aguardar auto-preenchimento ViaCEP
    await page.waitForTimeout(2000);
    await expect(page.locator('input[placeholder*="logradouro"]')).toHaveValue("RUA CAPITAO...");

    // 6. Verificar geocoding (coordenadas)
    // ... verificar se latitude/longitude foram preenchidas ...

    // 7. Completar cadastro e submeter
    const saveBtn = page.getByRole("button", { name: /salvar/i });
    await saveBtn.click();

    // 8. Verificar sucesso
    await expect(page.getByText("Empresa cadastrada com sucesso")).toBeVisible();
});
```

#### Cenário: Cadastro com Falha em Serviço Externo
**Testes de Integração:**
```python
async def test_criar_empresa_receita_indisponivel():
    # Arrange: Mock Receita Federal indisponível
    # Act: Criar empresa com CNPJ
    # Assert: Empresa criada mesmo sem enriquecimento (fallback)
    # Verificar logs de warning sobre falha no serviço externo
```

#### Cenário: Cadastro com CEP Inválido
```python
async def test_criar_empresa_cep_invalido():
    # Arrange: CEP inexistente
    # Act: Criar empresa
    # Assert: Empresa criada, mas endereço não enriquecido
    # Verificar logs sobre CEP inválido
```

---

### 📝 3. CRIAÇÃO DE EMPRESA (INTEGRANDO SERVIÇOS EXTERNOS)

---

### 📝 2. CRIAÇÃO DE EMPRESA
**Endpoint:** `POST /api/v1/companies/complete`

#### Cenário: Cadastro Completo (Caminho Feliz)
**Fluxo:** CNPJ válido → Dados Receita Federal → Contatos → Endereço → Submissão

**Testes de Integração (Backend):**
```python
# backend/tests/integration/test_company_complete.py
async def test_criar_empresa_completa_sucesso():
    # Arrange: Dados completos válidos
    company_data = {
        "pj_profile": {"name": "...", "tax_id": "11.222.333/0001-44"},
        "addresses": [{"street": "...", "is_principal": True}],
        "phones": [{"number": "...", "is_principal": True}],
        "emails": [{"email_address": "...", "is_principal": True}]
    }

    # Act: POST /api/v1/companies/complete
    response = await client.post("/api/v1/companies/complete", json=company_data)

    # Assert: 201 + IDs criados + dados no banco
    assert response.status_code == 201
    assert "new_company_id" in response.json()
    # Verificar tabelas: companies, people, pj_profiles, addresses, phones, emails
```

**Testes E2E (Frontend):**
```typescript
// frontend/e2e/company-crud-flow.spec.ts
test("fluxo completo CRUD empresa", async ({ page }) => {
    // 1. Login
    // 2. Navegar para criação
    // 3. Preencher CNPJ + consultar Receita
    // 4. Preencher contatos e endereço
    // 5. Submeter formulário
    // 6. Verificar criação + redirecionamento
    // 7. Verificar detalhes da empresa criada
    // 8. Editar empresa
    // 9. Verificar atualização
    // 10. Excluir empresa
    // 11. Verificar exclusão
});
```

#### Cenários de Erro (Caminhos Tristes)

**2.1 CNPJ Duplicado:**
```python
async def test_criar_empresa_cnpj_duplicado():
    # Arrange: CNPJ já existente
    # Act: POST com CNPJ duplicado
    # Assert: 400 + mensagem "CNPJ já cadastrado"
```

**2.2 Dados Obrigatórios Faltando:**
```python
async def test_criar_empresa_dados_invalidos():
    # Arrange: Faltando razão social
    # Act: POST sem campos obrigatórios
    # Assert: 422 + validações Pydantic
```

**2.3 Endereço sem Número:**
```python
async def test_criar_empresa_endereco_sem_numero():
    # Arrange: Endereço sem number
    # Act: POST
    # Assert: Modal de confirmação no frontend
```

---

### 📋 3. LISTAGEM DE EMPRESAS
**Endpoint:** `GET /api/v1/companies/complete-list`

#### Cenário: Listagem Básica
**Testes de Integração:**
```python
async def test_listar_empresas_paginacao():
    # Arrange: Múltiplas empresas no banco
    # Act: GET /complete-list?skip=0&limit=10
    # Assert: 200 + lista paginada + total count
```

#### Cenário: Filtros e Busca
```python
async def test_listar_empresas_filtros():
    # Arrange: Empresas com diferentes status/cidades
    # Act: GET /complete-list?access_status=active&city=São Paulo
    # Assert: Apenas empresas filtradas retornadas
```

---

### 👁️ 4. DETALHES DA EMPRESA
**Endpoint:** `GET /api/v1/companies/{id}`

#### Cenário: Empresa Existente
```python
async def test_detalhes_empresa_existente():
    # Arrange: Empresa criada
    # Act: GET /companies/{id}
    # Assert: 200 + dados completos mascarados (LGPD)
```

#### Cenário: Empresa Inexistente
```python
async def test_detalhes_empresa_inexistente():
    # Act: GET /companies/99999
    # Assert: 404 + mensagem "Empresa não encontrada"
```

---

### ✏️ 5. ATUALIZAÇÃO DE EMPRESA
**Endpoint:** `PUT /api/v1/companies/{id}/complete`

#### Cenário: Atualização Completa
```python
async def test_atualizar_empresa_completa():
    # Arrange: Empresa existente + novos dados
    # Act: PUT /companies/{id}/complete
    # Assert: 200 + dados atualizados no banco
```

#### Cenário: Atualização Parcial
```python
async def test_atualizar_empresa_parcial():
    # Arrange: Apenas alguns campos
    # Act: PUT com dados parciais
    # Assert: Apenas campos enviados atualizados
```

---

### 🗑️ 6. EXCLUSÃO DE EMPRESA
**Endpoint:** `DELETE /api/v1/companies/{id}`

#### Cenário: Soft Delete
```python
async def test_excluir_empresa():
    # Arrange: Empresa existente
    # Act: DELETE /companies/{id}
    # Assert: 204 + deleted_at preenchido (soft delete)
```

#### Cenário: Reativação
```python
async def test_reativar_empresa():
    # Arrange: Empresa excluída
    # Act: POST /companies/{id}/reactivate
    # Assert: 200 + deleted_at = null
```

---

### 🔍 7. BUSCA POR CNPJ
**Endpoint:** `GET /api/v1/companies/cnpj/{cnpj}`

#### Cenário: CNPJ Existente
```python
async def test_buscar_por_cnpj_existente():
    # Arrange: Empresa com CNPJ conhecido
    # Act: GET /cnpj/11.222.333/0001-44
    # Assert: 200 + dados da empresa
```

#### Cenário: CNPJ Inexistente
```python
async def test_buscar_por_cnpj_inexistente():
    # Act: GET /cnpj/99.999.999/0001-99
    # Assert: 404 + "Empresa não encontrada"
```

---

### ✅ 8. VALIDAÇÃO CNPJ
**Endpoint:** `GET /api/v1/companies/validate/cnpj/{cnpj}`

#### Cenário: CNPJ Disponível
```python
async def test_validar_cnpj_disponivel():
    # Act: GET /validate/cnpj/11.222.333/0001-44
    # Assert: 200 + {"exists": false}
```

#### Cenário: CNPJ Já Cadastrado
```python
async def test_validar_cnpj_cadastrado():
    # Arrange: CNPJ existente
    # Act: GET /validate/cnpj/{cnpj}
    # Assert: 200 + {"exists": true, "company_id": 123}
```

---

### 📞 9. CONTATOS DA EMPRESA
**Endpoint:** `GET /api/v1/companies/{id}/contacts`

#### Cenário: Empresa com Contatos
```python
async def test_contatos_empresa():
    # Arrange: Empresa com phones/emails
    # Act: GET /companies/{id}/contacts
    # Assert: 200 + JSON com telefones e emails agregados
```

---

### 🔒 10. FUNCIONALIDADES LGPD

#### 10.1 Audit Log
**Endpoint:** `GET /api/v1/lgpd/companies/{id}/audit-log`

```python
async def test_audit_log_empresa():
    # Arrange: Ações LGPD realizadas
    # Act: GET /audit-log?page=1&size=50
    # Assert: 200 + lista paginada de ações
```

#### 10.2 Reveal Campo
**Endpoint:** `POST /api/v1/lgpd/companies/{id}/reveal-field`

```python
async def test_reveal_campo_sensivel():
    # Arrange: Campo mascarado (ex: tax_id)
    # Act: POST /reveal-field?field_name=tax_id
    # Assert: 200 + campo revelado + log auditado
```

#### 10.3 Reveal Múltiplos Campos
**Endpoint:** `POST /api/v1/lgpd/companies/{id}/reveal-fields`

```python
async def test_reveal_multiplos_campos():
    # Arrange: Vários campos mascarados
    # Act: POST /reveal-fields com lista de campos
    # Assert: 200 + campos revelados + logs individuais
```

---

## 🛡️ 4. TESTES DE RESILIÊNCIA E FALLBACK

### Cenário: Serviços Externos Indisponíveis
**Testes de Integração:**
```python
async def test_cadastro_empresa_sem_servicos_externos():
    # Arrange: Mock todos os serviços externos como indisponíveis
    # ViaCEP, Receita Federal, Geocoding retornam erro/timeout

    # Act: Criar empresa
    response = await client.post("/api/v1/companies/complete", json=company_data)

    # Assert: Empresa criada com dados básicos apenas
    # Verificar logs de warning sobre falhas nos serviços externos
    # Verificar que processo não falhou completamente
```

### Cenário: Timeout em APIs Externas
```python
async def test_cadastro_empresa_timeout_externo():
    # Arrange: Mock timeout de 30s nas APIs externas
    # Act: Criar empresa com timeout
    # Assert: Sistema não fica travado, continua processamento
    # Empresa criada sem enriquecimento
```

### Cenário: Rate Limiting em APIs Externas
```python
async def test_cadastro_empresa_rate_limit_externo():
    # Arrange: Mock rate limit (429) nas APIs externas
    # Act: Criar empresa
    # Assert: Sistema trata erro graciosamente
    # Empresa criada, logs de rate limit
```

---

## 🎬 CENÁRIOS E2E COMPLETOS

### Cenário 1: Fluxo CRUD Completo
**Arquivo:** `frontend/e2e/company-crud-complete.spec.ts`

1. **Login** como admin
2. **Criar** empresa completa
3. **Listar** empresas (verificar nova empresa)
4. **Visualizar** detalhes (verificar dados mascarados)
5. **Reveal** campo sensível (verificar auditoria)
6. **Editar** empresa
7. **Verificar** atualização
8. **Excluir** empresa
9. **Verificar** exclusão na listagem

### Cenário 2: Validações de Negócio
**Arquivo:** `frontend/e2e/company-validations.spec.ts`

1. **Tentativa CNPJ duplicado** → Erro esperado
2. **Dados obrigatórios faltando** → Validações frontend
3. **Formato inválido** → Máscaras e validações
4. **Endereço sem número** → Modal de confirmação

### Cenário 3: Funcionalidades LGPD
**Arquivo:** `frontend/e2e/company-lgpd.spec.ts`

1. **Visualizar dados mascarados**
2. **Reveal campo individual**
3. **Reveal múltiplos campos**
4. **Verificar audit log**
5. **Tentativa sem permissão** → Acesso negado

---

## 📊 MÉTRICAS DE COBERTURA

### Backend (pytest)
- **Testes de Integração:** 15+ cenários por API crítica
- **Serviços Externos:** 10+ cenários (ViaCEP, Receita Federal, Geocoding)
- **Resiliência:** 5+ cenários de fallback e erro
- **Cobertura Mínima:** 80% das linhas de código
- **Stored Procedures:** Testes de entrada/saída

### Frontend (Jest + Testing Library)
- **Componentes:** Testes de renderização + interações
- **Serviços:** Mocks para APIs externas + externas (ViaCEP, Receita)
- **Hooks:** Estados e efeitos
- **Enriquecimento:** Testes de auto-preenchimento

### E2E (Playwright)
- **Cenários Críticos:** 4 fluxos principais (CRUD + enriquecimento)
- **APIs Externas:** Testes de integração real com ViaCEP/Recepita
- **Navegadores:** Chrome, Firefox, Safari
- **Dispositivos:** Desktop, tablet, mobile
- **Fallback:** Cenários com serviços externos indisponíveis

---

## 🚀 EXECUÇÃO E AUTOMATIZAÇÃO

### Pipeline CI/CD
```yaml
# .github/workflows/test-companies.yml
name: Test CRUD Companies
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd backend
          pytest tests/integration/test_company* -v --cov=app --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm run test -- --coverage --testPathPattern=companies

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E Tests
        run: |
          cd frontend
          npx playwright test e2e/company-*.spec.ts
```

### Comandos Locais
```bash
# Backend - Todos os testes de empresa
cd backend && pytest tests/integration/test_company* -v

# Frontend - Testes unitários
cd frontend && npm run test -- --testPathPattern=companies

# E2E - Fluxos completos
cd frontend && npx playwright test e2e/company-crud-complete.spec.ts

# Cobertura combinada
cd backend && pytest --cov=app --cov-report=html
cd frontend && npm run test -- --coverage
```

---

## 📈 MONITORAMENTO E RELATÓRIOS

### Dashboard de Qualidade
- **Cobertura de Testes:** Target 85% backend, 80% frontend
- **Tempo de Execução:** < 5min para suite completa
- **Flaky Tests:** < 1% de testes instáveis
- **Bugs Produção:** Zero regressões em funcionalidades testadas

### Relatórios Automatizados
- **Cobertura:** HTML reports gerados em CI
- **Performance:** Métricas de tempo de resposta
- **Logs:** Captura de erros e falhas
- **Screenshots:** Para testes E2E com falha

---

## 📁 ESTRUTURA DE ARQUIVOS ATUALIZADA

### Novos Arquivos a Criar (Serviços Externos):

```
backend/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── cnpj.py                     # ✨ NOVO (consulta Receita Federal)
│   │   ├── geocoding.py                # ✨ NOVO (geocoding Nominatim)
│   │   └── geolocation.py              # ✨ NOVO (geolocation service)
│   ├── services/
│   │   ├── address_enrichment_service.py  # ✨ NOVO (ViaCEP integration)
│   │   └── cnpj_service.py             # ✨ NOVO (Receita Federal integration)
│   └── schemas/
│       ├── cnpj.py                     # ✨ NOVO
│       ├── geocoding.py                # ✨ NOVO
│       └── geolocation.py              # ✨ NOVO
├── tests/integration/
│   ├── test_external_services.py       # ✨ NOVO (ViaCEP, Receita, Geocoding)
│   ├── test_company_complete_with_external.py  # ✨ NOVO
│   └── test_resilience_external.py     # ✨ NOVO (fallback/errors)

frontend/
├── e2e/
│   ├── company-registration-with-external-apis.spec.ts  # ✨ NOVO
│   └── company-external-services-fallback.spec.ts       # ✨ NOVO
└── src/
    └── services/
        ├── addressService.ts           # ✨ NOVO (ViaCEP frontend)
        └── cnpjService.ts              # ✨ NOVO (Receita frontend)
```

### Arquivos a Atualizar:

```
backend/
├── app/api/v1/companies.py              # ✏️ Integrar enriquecimento automático
├── app/api/v1/router.py                 # ✏️ Registrar novos endpoints
└── tests/conftest.py                    # ✏️ Adicionar fixtures para serviços externos

frontend/
├── src/services/companiesService.ts     # ✏️ Adicionar chamadas para serviços externos
└── src/components/companies/            # ✏️ Atualizar componentes para auto-preenchimento
```

---

## 🎯 PRÓXIMOS PASSOS

### Semana 1: Serviços Externos - Backend
1. ✅ Implementar serviços ViaCEP, Receita Federal, Geocoding
2. ✅ Criar testes de integração para APIs externas
3. ✅ Implementar lógica de fallback e resiliência
4. ✅ Configurar pipeline CI para testes backend

### Semana 2: Integração CRUD + Externos
5. ✅ Integrar enriquecimento automático no cadastro de empresas
6. ✅ Criar testes E2E com APIs externas reais
7. ✅ Implementar testes de validação de formulários
8. ✅ Testes de fallback quando serviços externos falham

### Semana 3: Frontend + E2E Completo
9. ✅ Atualizar frontend para consumir serviços externos
10. ✅ Criar testes E2E para fluxos com enriquecimento
11. ✅ Automatizar pipeline completo
12. ✅ Testes de performance e carga

### Semana 4: LGPD + Monitoramento
13. ✅ Testes completos de funcionalidades LGPD
14. ✅ Dashboard de qualidade implementado
15. ✅ Alertas para falhas de teste
16. ✅ Métricas de cobertura atingidas

---

## ⚠️ RISCOS E MITIGAÇÕES

### Risco: Stored Procedures não testáveis
**Mitigação:** Criar testes de contrato (input/output) + mocks

### Risco: Dados LGPD em testes
**Mitigação:** Usar dados fictícios + limpeza automática

### Risco: Testes E2E flaky
**Mitigação:** Esperas inteligentes + isolamento de testes

### Risco: Manutenção alta
**Mitigação:** Padrões consistentes + Page Objects

---

**Estimativa Total:** 5-6 semanas (incluindo serviços externos)  
**Equipe:** 2-3 desenvolvedores (1 backend, 1 frontend, 1 QA opcional)  
**Prioridade:** ALTA - Fundacional para qualidade do sistema  
**Complexidade:** MÉDIA-ALTA (integração com 3 APIs externas + resiliência)