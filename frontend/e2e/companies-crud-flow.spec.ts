// frontend/e2e/companies-crud-flow.spec.ts
/**
 * Testes E2E para fluxo completo de CRUD de empresas
 * Baseado no fluxo validado no backend (18/18 testes passando)
 */

import { test, expect, Page } from '@playwright/test';

// Configuração de dados de teste
const TEST_COMPANY = {
  cnpj: '14337098000185', // Hospital Unimed - AL (validado no backend)
  razao_social: 'HOSPITAL UNIMED LTDA',
  nome_fantasia: 'HOSPITAL UNIMED',
  telefone: '(82) 99999-9999',
  email: 'contato@hospitalunimed.com.br',
  cep: '57035000',
  logradouro: 'AVENIDA FERNANDES LIMA',
  numero: '1234',
  bairro: 'FAROL',
  cidade: 'MACEIÓ',
  uf: 'AL'
};

class CompaniesPage {
  constructor(public page: Page) {}
  
  // Seletores
  get listTable() { return this.page.locator('[data-testid="companies-table"]'); }
  get addButton() { return this.page.locator('[data-testid="add-company-btn"]'); }
  get searchInput() { return this.page.locator('[data-testid="search-input"]'); }
  get statusFilter() { return this.page.locator('[data-testid="status-filter"]'); }
  
  // Formulário
  get cnpjInput() { return this.page.locator('[data-testid="cnpj-input"]'); }
  get consultCnpjBtn() { return this.page.locator('[data-testid="consult-cnpj-btn"]'); }
  get razaoSocialInput() { return this.page.locator('[data-testid="razao-social-input"]'); }
  get nomeFantasiaInput() { return this.page.locator('[data-testid="nome-fantasia-input"]'); }
  get telefoneInput() { return this.page.locator('[data-testid="telefone-input"]'); }
  get emailInput() { return this.page.locator('[data-testid="email-input"]'); }
  get cepInput() { return this.page.locator('[data-testid="cep-input"]'); }
  get saveButton() { return this.page.locator('[data-testid="save-company-btn"]'); }
  
  // Ações
  async navigateToCompanies() {
    await this.page.goto('/companies');
    await expect(this.page.locator('h1')).toContainText('Empresas');
  }
  
  async waitForTableLoad() {
    await expect(this.listTable).toBeVisible();
    // Aguardar loading desaparecer
    await this.page.waitForSelector('[data-testid="loading-spinner"]', { state: 'hidden' });
  }
  
  async searchCompany(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.keyboard.press('Enter');
    await this.waitForTableLoad();
  }
  
  async openAddForm() {
    await this.addButton.click();
    await expect(this.page.locator('[data-testid="company-form"]')).toBeVisible();
  }
  
  async fillCnpjAndConsult(cnpj: string) {
    await this.cnpjInput.fill(cnpj);
    await this.consultCnpjBtn.click();
    
    // Aguardar preenchimento automático
    await expect(this.razaoSocialInput).not.toHaveValue('');
  }
  
  async fillCompanyForm(data: typeof TEST_COMPANY) {
    // Preencher dados básicos
    await this.nomeFantasiaInput.fill(data.nome_fantasia);
    await this.telefoneInput.fill(data.telefone);
    await this.emailInput.fill(data.email);
    
    // Preencher endereço
    await this.cepInput.fill(data.cep);
    // Aguardar preenchimento automático do endereço
    await this.page.waitForTimeout(1000);
    
    // Preencher número
    await this.page.locator('[data-testid="numero-input"]').fill(data.numero);
  }
  
  async saveCompany() {
    await this.saveButton.click();
    
    // Aguardar toast de sucesso
    await expect(this.page.locator('.toast')).toContainText('sucesso');
    
    // Aguardar redirecionamento para lista
    await this.waitForTableLoad();
  }
  
  async getCompanyRowByCnpj(cnpj: string) {
    // Buscar linha da tabela que contém o CNPJ (pode estar mascarado)
    const cnpjFormatted = cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    return this.page.locator(`tr:has-text("${cnpjFormatted.substring(0, 8)}")`).first();
  }
  
  async openCompanyDetails(cnpj: string) {
    const row = await this.getCompanyRowByCnpj(cnpj);
    await row.locator('[data-testid="view-btn"]').click();
    
    await expect(this.page.locator('[data-testid="company-details"]')).toBeVisible();
  }
  
  async revealSensitiveData() {
    await this.page.locator('[data-testid="reveal-data-btn"]').click();
    
    // Aguardar confirmação
    await this.page.locator('[data-testid="confirm-reveal-btn"]').click();
    
    // Aguardar dados serem revelados
    await expect(this.page.locator('[data-testid="cnpj-revealed"]')).toBeVisible();
  }
  
  async checkLgpdLogs() {
    await this.page.locator('[data-testid="lgpd-logs-tab"]').click();
    
    // Verificar se há logs
    await expect(this.page.locator('[data-testid="lgpd-logs-table"]')).toBeVisible();
    await expect(this.page.locator('tr:has-text("REVEAL")')).toBeVisible();
  }
  
  async editCompany() {
    await this.page.locator('[data-testid="edit-btn"]').click();
    
    // Alterar nome fantasia
    const newName = `${TEST_COMPANY.nome_fantasia} - EDITADO`;
    await this.nomeFantasiaInput.fill(newName);
    
    await this.saveButton.click();
    
    // Aguardar toast de sucesso
    await expect(this.page.locator('.toast')).toContainText('atualizada');
    
    return newName;
  }
  
  async deactivateCompany() {
    await this.page.locator('[data-testid="deactivate-btn"]').click();
    
    // Confirmar inativação
    await this.page.locator('[data-testid="confirm-deactivate-btn"]').click();
    
    // Aguardar toast de sucesso
    await expect(this.page.locator('.toast')).toContainText('inativada');
  }
  
  async activateCompany() {
    await this.page.locator('[data-testid="activate-btn"]').click();
    
    // Aguardar toast de sucesso
    await expect(this.page.locator('.toast')).toContainText('ativada');
  }
  
  async filterByStatus(status: 'active' | 'inactive') {
    await this.statusFilter.selectOption(status);
    await this.waitForTableLoad();
  }
}

test.describe('Fluxo Completo CRUD de Empresas', () => {
  let companiesPage: CompaniesPage;
  
  test.beforeEach(async ({ page }) => {
    companiesPage = new CompaniesPage(page);
    
    // Login (assumindo que existe um sistema de auth)
    await page.goto('/login');
    await page.locator('[data-testid="email-input"]').fill('admin@proteancare.com');
    await page.locator('[data-testid="password-input"]').fill('admin123');
    await page.locator('[data-testid="login-btn"]').click();
    
    // Aguardar redirecionamento
    await expect(page).toHaveURL(/\/dashboard/);
  });
  
  test('1. Deve listar empresas existentes', async () => {
    await companiesPage.navigateToCompanies();
    await companiesPage.waitForTableLoad();
    
    // Verificar se tabela está visível
    await expect(companiesPage.listTable).toBeVisible();
    
    // Verificar se há pelo menos cabeçalhos
    await expect(companiesPage.page.locator('th:has-text("CNPJ")')).toBeVisible();
    await expect(companiesPage.page.locator('th:has-text("Razão Social")')).toBeVisible();
  });
  
  test('2. Deve criar nova empresa com consulta CNPJ', async () => {
    await companiesPage.navigateToCompanies();
    await companiesPage.openAddForm();
    
    // Consultar CNPJ
    await companiesPage.fillCnpjAndConsult(TEST_COMPANY.cnpj);
    
    // Verificar preenchimento automático
    await expect(companiesPage.razaoSocialInput).toHaveValue(TEST_COMPANY.razao_social);
    
    // Preencher dados adicionais
    await companiesPage.fillCompanyForm(TEST_COMPANY);
    
    // Salvar
    await companiesPage.saveCompany();
    
    // Verificar se empresa aparece na lista
    const companyRow = await companiesPage.getCompanyRowByCnpj(TEST_COMPANY.cnpj);
    await expect(companyRow).toBeVisible();
  });
  
  test('3. Deve consultar empresa criada e verificar dados', async () => {
    await companiesPage.navigateToCompanies();
    
    // Buscar empresa específica
    await companiesPage.searchCompany(TEST_COMPANY.nome_fantasia);
    
    // Abrir detalhes
    await companiesPage.openCompanyDetails(TEST_COMPANY.cnpj);
    
    // Verificar dados mascarados
    await expect(companiesPage.page.locator('[data-testid="cnpj-masked"]')).toContainText('****');
    await expect(companiesPage.page.locator('[data-testid="email-masked"]')).toContainText('****');
    
    // Verificar dados não sensíveis
    await expect(companiesPage.page.locator('[data-testid="razao-social"]')).toContainText(TEST_COMPANY.razao_social);
  });
  
  test('4. Deve revelar dados sensíveis e verificar logs LGPD', async () => {
    await companiesPage.navigateToCompanies();
    await companiesPage.searchCompany(TEST_COMPANY.nome_fantasia);
    await companiesPage.openCompanyDetails(TEST_COMPANY.cnpj);
    
    // Revelar dados
    await companiesPage.revealSensitiveData();
    
    // Verificar dados revelados
    await expect(companiesPage.page.locator('[data-testid="cnpj-revealed"]')).toContainText(TEST_COMPANY.cnpj);
    
    // Verificar logs LGPD
    await companiesPage.checkLgpdLogs();
  });
  
  test('5. Deve editar empresa existente', async () => {
    await companiesPage.navigateToCompanies();
    await companiesPage.searchCompany(TEST_COMPANY.nome_fantasia);
    await companiesPage.openCompanyDetails(TEST_COMPANY.cnpj);
    
    // Editar empresa
    const newName = await companiesPage.editCompany();
    
    // Verificar alteração na lista
    await companiesPage.navigateToCompanies();
    await companiesPage.searchCompany(newName);
    
    const companyRow = await companiesPage.getCompanyRowByCnpj(TEST_COMPANY.cnpj);
    await expect(companyRow).toContainText(newName);
  });
  
  test('6. Deve inativar e ativar empresa', async () => {
    await companiesPage.navigateToCompanies();
    await companiesPage.searchCompany(TEST_COMPANY.nome_fantasia);
    await companiesPage.openCompanyDetails(TEST_COMPANY.cnpj);
    
    // Inativar empresa
    await companiesPage.deactivateCompany();
    
    // Verificar que não aparece na lista ativa
    await companiesPage.navigateToCompanies();
    await companiesPage.filterByStatus('active');
    
    const activeRow = companiesPage.page.locator(`tr:has-text("${TEST_COMPANY.cnpj.substring(0, 8)}")`);
    await expect(activeRow).not.toBeVisible();
    
    // Verificar que aparece na lista inativa
    await companiesPage.filterByStatus('inactive');
    
    const inactiveRow = await companiesPage.getCompanyRowByCnpj(TEST_COMPANY.cnpj);
    await expect(inactiveRow).toBeVisible();
    
    // Reativar empresa
    await companiesPage.openCompanyDetails(TEST_COMPANY.cnpj);
    await companiesPage.activateCompany();
    
    // Verificar que voltou para lista ativa
    await companiesPage.navigateToCompanies();
    await companiesPage.filterByStatus('active');
    
    const reactivatedRow = await companiesPage.getCompanyRowByCnpj(TEST_COMPANY.cnpj);
    await expect(reactivatedRow).toBeVisible();
  });
  
  test('7. Deve validar filtros e busca', async () => {
    await companiesPage.navigateToCompanies();
    
    // Testar busca
    await companiesPage.searchCompany('HOSPITAL');
    
    // Verificar que resultados contêm o termo
    const rows = companiesPage.page.locator('tbody tr');
    const count = await rows.count();
    
    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const row = rows.nth(i);
        await expect(row).toContainText(/HOSPITAL/i);
      }
    }
    
    // Testar filtros de status
    await companiesPage.filterByStatus('active');
    await companiesPage.waitForTableLoad();
    
    await companiesPage.filterByStatus('inactive');
    await companiesPage.waitForTableLoad();
  });
});

// Configuração de cleanup
test.afterEach(async ({ page }) => {
  // Limpar dados de teste se necessário
  // (Opcional: remover empresa criada nos testes)
});
