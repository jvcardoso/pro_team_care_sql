# 🚀 ROADMAP DE IMPLEMENTAÇÃO - Testes CRUD Empresas com Serviços Externos

**Data:** 28/10/2025
**Objetivo:** Implementação sequencial e organizada do plano de testes
**Metodologia:** Tarefas pequenas, independentes, com validação clara

---

## 📋 ESTRATÉGIA DE EXECUÇÃO

### Princípios:
- **Tarefas Pequenas:** Cada tarefa deve ser completável em 1-2 dias
- **Validação Clara:** Cada tarefa tem critérios de aceitação específicos
- **Dependências Explícitas:** Tarefas só começam quando dependências estão prontas
- **Testes Contínuos:** Executar testes relevantes após cada tarefa
- **Documentação:** Atualizar documentação conforme implementação

### Ordem de Prioridade:
1. **Backend Core** (serviços externos)
2. **Integração Backend**
3. **Frontend Services**
4. **Testes E2E**
5. **Integração Final**

---

## 🔥 FASE 1: BACKEND - SERVIÇOS EXTERNOS (Semanas 1-2)

### 🎯 Objetivo: Implementar infraestrutura de serviços externos

#### 1.1 ViaCEP Service
**Tarefa:** `backend_external_viacep_service`
**Arquivo:** `backend/app/services/address_enrichment_service.py`

**Dependências:** Nenhuma

**Implementação:**
```python
class AddressEnrichmentService:
    def __init__(self):
        self.viacep_base_url = "https://viacep.com.br/ws"
        self.timeout = httpx.Timeout(10.0)
        self.cache = {}  # Cache em memória

    async def consult_viacep(self, cep: str) -> Optional[Dict[str, Any]]:
        # Validação de CEP
        # Cache check
        # Chamada HTTP para ViaCEP
        # Parsing e validação de resposta
        # Tratamento de erros
        # Cache storage
        pass
```

**Critérios de Aceitação:**
- ✅ Método `consult_viacep()` implementado
- ✅ Validação de formato de CEP
- ✅ Cache funcionando (mesmo CEP não faz nova chamada)
- ✅ Tratamento de CEP inexistente
- ✅ Tratamento de timeout/erros de rede
- ✅ Logs apropriados para debugging

**Teste Manual:**
```bash
cd backend
python -c "
import asyncio
from app.services.address_enrichment_service import AddressEnrichmentService

async def test():
    service = AddressEnrichmentService()
    result = await service.consult_viacep('01001000')
    print('ViaCEP result:', result)

asyncio.run(test())
"
```

#### 1.2 Receita Federal Service
**Tarefa:** `backend_external_receita_service`
**Arquivo:** `backend/app/services/cnpj_service.py`

**Dependências:** Nenhuma

**Implementação:**
```python
class CNPJService:
    def __init__(self):
        self.receita_base_url = "https://receitaws.com.br/v1"
        self.timeout = httpx.Timeout(15.0)  # Receita pode ser mais lenta

    async def consultar_receita(self, cnpj: str) -> CNPJConsultaResponse:
        # Limpeza e validação do CNPJ
        # Chamada para ReceitaWS
        # Parsing da resposta
        # Mapeamento para estrutura interna
        # Tratamento de erros específicos da Receita
        pass
```

**Critérios de Aceitação:**
- ✅ Método `consultar_receita()` implementado
- ✅ Validação de CNPJ (formato e dígito verificador)
- ✅ Parsing correto dos dados da Receita
- ✅ Tratamento de CNPJ inexistente
- ✅ Tratamento de rate limiting da Receita
- ✅ Mapeamento para estrutura interna do sistema

#### 1.3 Geocoding Service
**Tarefa:** `backend_external_geocoding_service`
**Arquivo:** `backend/app/api/v1/endpoints/geocoding.py`

**Dependências:** Nenhuma

**Implementação:**
```python
class GeocodingService:
    def __init__(self):
        self.nominatim_base_url = "https://nominatim.openstreetmap.org"
        self.rate_limit_delay = 1.0  # 1 segundo entre requests

    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        # Rate limiting
        # Construção da query para Nominatim
        # Chamada HTTP
        # Parsing das coordenadas
        # Cálculo de precisão
        # Tratamento de endereços não encontrados
        pass
```

**Critérios de Aceitação:**
- ✅ Rate limiting implementado (1s entre requests)
- ✅ Parsing correto de latitude/longitude
- ✅ Cálculo de precisão baseado no tipo de resultado
- ✅ Tratamento de endereços não encontrados
- ✅ Headers apropriados (User-Agent)

---

## 🧪 FASE 2: BACKEND - TESTES DE SERVIÇOS EXTERNOS (Semana 2)

### 🎯 Objetivo: Criar testes robustos para serviços externos

#### 2.1 Testes ViaCEP
**Tarefa:** `backend_tests_external_viacep`
**Arquivo:** `backend/tests/integration/test_external_services.py`

**Dependências:** ViaCEP service implementado

**Cenários de Teste:**
```python
async def test_consultar_cep_valido():
    # CEP real que existe
    result = await service.consult_viacep("01001000")
    assert result is not None
    assert result["logradouro"] == "Praça da Sé"
    assert result["localidade"] == "São Paulo"

async def test_consultar_cep_invalido():
    # CEP que não existe
    result = await service.consult_viacep("99999999")
    assert result is None

async def test_consultar_cep_cache():
    # Primeiro acesso (chama API)
    result1 = await service.consult_viacep("01001000")

    # Segundo acesso (usa cache)
    result2 = await service.consult_viacep("01001000")

    # Mesmo resultado, sem nova chamada
    assert result1 == result2
```

#### 2.2 Testes Receita Federal
**Tarefa:** `backend_tests_external_receita`
**Arquivo:** `backend/tests/integration/test_external_services.py`

**Cenários de Teste:**
```python
async def test_consultar_cnpj_valido():
    # CNPJ real (usar um de teste conhecido)
    result = await service.consultar_receita("11222333000144")
    assert result.success is True
    assert "nome" in result.data
    assert "fantasia" in result.data

async def test_consultar_cnpj_inexistente():
    result = await service.consultar_receita("99999999000199")
    assert result.success is False
    assert "não encontrado" in result.message.lower()
```

#### 2.3 Testes de Resiliência
**Tarefa:** `backend_tests_external_resilience`
**Arquivo:** `backend/tests/integration/test_resilience_external.py`

**Cenários de Teste:**
```python
async def test_viacep_timeout():
    # Mock timeout de 30 segundos
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = asyncio.TimeoutError()

        result = await service.consult_viacep("01001000")
        assert result is None  # Deve retornar None graciosamente

async def test_receita_rate_limit():
    # Mock resposta de rate limit (429)
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        result = await service.consultar_receita("11222333000144")
        assert result.success is False
        # Verificar se logou o erro apropriadamente
```

---

## 🔗 FASE 3: BACKEND - INTEGRAÇÃO COM CRUD (Semana 3)

### 🎯 Objetivo: Integrar serviços externos no fluxo de criação de empresas

#### 3.1 Integração no Endpoint
**Tarefa:** `backend_integration_company_creation`
**Arquivo:** `backend/app/api/v1/companies.py`

**Modificações:**
```python
@router.post("/complete", response_model=CompanyCompleteResponse)
async def create_company_complete(
    company_data: CompanyCompleteCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # ... validações existentes ...

    # NOVO: Enriquecimento automático
    enriched_data = await enrich_company_data(company_data)

    # ... resto do código ...
```

**Função de Enriquecimento:**
```python
async def enrich_company_data(company_data: CompanyCompleteCreate) -> Dict[str, Any]:
    """Enriquece dados da empresa com serviços externos"""
    enriched = company_data.model_dump()

    # 1. Consultar Receita Federal se CNPJ fornecido
    if company_data.pj_profile.tax_id:
        receita_data = await cnpj_service.consultar_receita(company_data.pj_profile.tax_id)
        if receita_data.success:
            # Mesclar dados da Receita
            enriched["pj_profile"].update(map_receita_to_pj_profile(receita_data.data))

    # 2. Consultar ViaCEP se endereço com CEP fornecido
    for address in enriched.get("addresses", []):
        if address.get("zip_code"):
            viacep_data = await address_service.consult_viacep(address["zip_code"])
            if viacep_data:
                # Mesclar dados do ViaCEP
                address.update(map_viacep_to_address(viacep_data))

                # 3. Geocoding do endereço completo
                full_address = build_full_address(address)
                geo_data = await geocoding_service.geocode_address(full_address)
                if geo_data:
                    address["latitude"] = geo_data["latitude"]
                    address["longitude"] = geo_data["longitude"]

    return enriched
```

#### 3.2 Testes de Integração
**Tarefa:** `backend_integration_tests_enriched_creation`
**Arquivo:** `backend/tests/integration/test_company_complete_with_external.py`

**Cenários de Teste:**
```python
async def test_criar_empresa_com_enriquecimento_completo():
    # Arrange: Dados básicos + CEP/CNPJ válidos
    company_data = {
        "pj_profile": {
            "tax_id": "11222333000144",  # CNPJ que existe na Receita
            "name": "Empresa Teste"
        },
        "addresses": [{
            "zip_code": "01001000",  # CEP válido
            "number": "123"
        }],
        "phones": [{"number": "11999999999", "is_principal": True}],
        "emails": [{"email_address": "teste@empresa.com", "is_principal": True}]
    }

    # Act: Criar empresa
    response = await client.post("/api/v1/companies/complete", json=company_data)

    # Assert: Empresa criada com dados enriquecidos
    assert response.status_code == 201
    data = response.json()

    # Verificar que dados foram enriquecidos
    # PJ Profile tem dados da Receita
    # Address tem dados do ViaCEP + coordenadas
```

---

## 🎨 FASE 4: FRONTEND - SERVIÇOS E INTEGRAÇÃO (Semana 4)

### 🎯 Objetivo: Implementar frontend para consumir serviços externos

#### 4.1 Serviço ViaCEP Frontend
**Tarefa:** `frontend_external_address_service`
**Arquivo:** `frontend/src/services/addressService.ts`

**Implementação:**
```typescript
class AddressService {
  async consultarCEP(cep: string): Promise<ViaCEPResponse | null> {
    try {
      const cleanCEP = cep.replace(/\D/g, '');
      if (cleanCEP.length !== 8) return null;

      const response = await api.get(`https://viacep.com.br/ws/${cleanCEP}/json/`);
      if (response.data.erro) return null;

      return response.data;
    } catch (error) {
      console.error('Erro ao consultar CEP:', error);
      return null;
    }
  }
}
```

#### 4.2 Serviço Receita Federal Frontend
**Tarefa:** `frontend_external_cnpj_service`
**Arquivo:** `frontend/src/services/cnpjService.ts`

**Implementação:**
```typescript
class CNPJService {
  async consultarCNPJ(cnpj: string): Promise<CNPJResponse | null> {
    try {
      const cleanCNPJ = cnpj.replace(/\D/g, '');
      if (cleanCNPJ.length !== 14) return null;

      const response = await api.get(`https://receitaws.com.br/v1/cnpj/${cleanCNPJ}`);
      if (response.data.status === 'ERROR') return null;

      return response.data;
    } catch (error) {
      console.error('Erro ao consultar CNPJ:', error);
      return null;
    }
  }
}
```

#### 4.3 Integração no Company Service
**Tarefa:** `frontend_integration_companies_service`
**Arquivo:** `frontend/src/services/companiesService.ts`

**Modificações:**
```typescript
class CompaniesService {
  async createWithEnrichment(data: CompanyCreateData): Promise<CompanyResponse> {
    // 1. Se CNPJ fornecido, consultar Receita
    if (data.pj_profile?.tax_id) {
      const receitaData = await cnpjService.consultarCNPJ(data.pj_profile.tax_id);
      if (receitaData) {
        // Auto-preencher dados da Receita
        data.pj_profile = {
          ...data.pj_profile,
          name: receitaData.nome || data.pj_profile.name,
          trade_name: receitaData.fantasia || data.pj_profile.trade_name,
          // ... outros campos
        };
      }
    }

    // 2. Para cada endereço com CEP, consultar ViaCEP
    if (data.addresses) {
      for (const address of data.addresses) {
        if (address.zip_code) {
          const viacepData = await addressService.consultarCEP(address.zip_code);
          if (viacepData) {
            // Auto-preencher endereço
            address.street = viacepData.logradouro || address.street;
            address.neighborhood = viacepData.bairro || address.neighborhood;
            address.city = viacepData.localidade || address.city;
            address.state = viacepData.uf || address.state;
          }
        }
      }
    }

    // 3. Criar empresa com dados enriquecidos
    return this.create(data);
  }
}
```

---

## 🧪 FASE 5: TESTES E2E COMPLETOS (Semana 5)

### 🎯 Objetivo: Validar fluxos completos com APIs externas

#### 5.1 Teste E2E com Enriquecimento
**Tarefa:** `frontend_tests_e2e_enriched_registration`
**Arquivo:** `frontend/e2e/company-registration-with-external-apis.spec.ts`

**Cenário Principal:**
```typescript
test("cadastro empresa com enriquecimento automático", async ({ page }) => {
  // 1. Login
  await page.goto("/login");
  // ... steps de login ...

  // 2. Navegar para formulário
  await page.goto("/admin/empresas?view=create");

  // 3. Preencher CNPJ e aguardar Receita
  const cnpjInput = page.getByLabel("CNPJ");
  await cnpjInput.fill("05.514.464/0001-30"); // CNPJ real

  const consultarBtn = page.getByRole("button", { name: /consultar/i });
  await consultarBtn.click();

  // 4. Verificar auto-preenchimento Receita
  await expect(page.getByLabel("Razão Social")).toHaveValue("BRAZIL HOME CARE...");
  await expect(page.getByLabel("Nome Fantasia")).toHaveValue("DOMICILE HOME CARE");

  // 5. Preencher CEP e aguardar ViaCEP
  const cepInput = page.locator('input[placeholder*="CEP"]').first();
  await cepInput.fill("13201840");

  await page.waitForTimeout(2000); // Aguardar ViaCEP

  // 6. Verificar auto-preenchimento ViaCEP
  await expect(page.locator('input[placeholder*="logradouro"]')).toHaveValue("RUA CAPITAO...");

  // 7. Completar e submeter
  const saveBtn = page.getByRole("button", { name: /salvar/i });
  await saveBtn.click();

  // 8. Verificar sucesso
  await expect(page.getByText("Empresa cadastrada com sucesso")).toBeVisible();
});
```

#### 5.2 Teste E2E de Fallback
**Tarefa:** `frontend_tests_e2e_fallback_scenarios`
**Arquivo:** `frontend/e2e/company-external-services-fallback.spec.ts`

**Cenário de Fallback:**
```typescript
test("cadastro empresa com serviços externos indisponíveis", async ({ page }) => {
  // 1. Mock/simular APIs externas offline
  await page.route('https://receitaws.com.br/**', route => route.abort());
  await page.route('https://viacep.com.br/**', route => route.abort());

  // 2. Tentar cadastro normal
  // 3. Verificar que continua funcionando sem enriquecimento
  // 4. Empresa criada com dados manuais apenas
  // 5. Verificar mensagens de aviso sobre falha nos serviços
});
```

---

## ✅ FASE 6: INTEGRAÇÃO FINAL E VALIDAÇÃO (Semana 6)

### 🎯 Objetivo: Validar sistema completo e configurar CI/CD

#### 6.1 Execução Completa de Testes
**Tarefas:** `integration_full_backend_test_run`, `integration_full_frontend_test_run`, `integration_full_e2e_test_run`

**Comandos:**
```bash
# Backend
cd backend && pytest tests/integration/ -v --tb=short

# Frontend Unit
cd frontend && npm run test -- --watchAll=false

# E2E
cd frontend && npx playwright test e2e/company-*.spec.ts --headed
```

#### 6.2 Pipeline CI/CD
**Tarefa:** `integration_ci_cd_pipeline`
**Arquivo:** `.github/workflows/test-companies.yml`

```yaml
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
          pytest --cov=app --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm run test -- --coverage

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E Tests
        run: |
          cd frontend
          npx playwright test e2e/company-*.spec.ts
```

#### 6.3 Relatórios de Cobertura
**Tarefa:** `integration_coverage_reports`

**Métricas Mínimas:**
- Backend: 80% cobertura
- Frontend: 75% cobertura
- E2E: Todos os fluxos críticos passando

---

## 📊 ACOMPANHAMENTO E MÉTRICAS

### Dashboard de Progresso
- ✅ Tarefas concluídas
- 🔄 Tarefas em andamento
- ⏳ Tarefas pendentes
- 📈 Cobertura de testes
- 🚨 Falhas críticas

### Critérios de Pronto
- [ ] Todos os testes passando
- [ ] Cobertura mínima atingida
- [ ] Pipeline CI/CD funcionando
- [ ] Documentação atualizada
- [ ] Fluxos E2E validados

### Plano de Contingência
- **Se API externa ficar indisponível:** Usar mocks e dados de teste
- **Se cobertura baixa:** Priorizar testes dos fluxos críticos
- **Se tempo apertado:** Implementar versão simplificada primeiro

---

## 🎯 PRÓXIMAS AÇÕES IMEDIATAS

1. **Começar com:** `backend_external_viacep_service`
2. **Tempo estimado:** 2-3 dias para primeira implementação
3. **Validação:** Teste manual + unitário básico
4. **Próxima:** `backend_external_receita_service`

**Lembre-se:** Qualidade > Velocidade. Cada tarefa deve estar 100% funcional antes de passar para a próxima.