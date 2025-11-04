/**
 * Testes E2E para cadastro de empresa com enriquecimento automático.
 *
 * Testa o fluxo completo: CNPJ → Receita Federal → CEP → ViaCEP → Geocoding → Submissão
 * Usa APIs externas reais para validar integração completa.
 */

import { test, expect } from '@playwright/test';

test.describe('Cadastro de Empresa com Enriquecimento Automático', () => {
  test.beforeEach(async ({ page }) => {
    // Login como admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@proteamcare.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Aguardar redirecionamento para dashboard
    await page.waitForURL('**/admin**');
  });

  test('deve cadastrar empresa com enriquecimento completo CNPJ + CEP', async ({ page }) => {
    // Navegar para formulário de empresa
    await page.goto('/admin/empresas?view=create');

    // Verificar que estamos na página correta
    await expect(page).toHaveURL(/.*empresas.*view=create/);
    await expect(page.locator('h1, h2')).toContainText(/nova empresa|cadastrar empresa/i);

    // Preencher CNPJ válido (usar um CNPJ real de teste)
    const cnpjInput = page.locator('input[placeholder*="CNPJ"], input[name*="cnpj"]').first();
    await cnpjInput.fill('05.514.464/0001-30'); // CNPJ real da Brazil Home Care

    // Aguardar consulta automática da Receita Federal
    await page.waitForTimeout(3000); // Dar tempo para a API responder

    // Verificar auto-preenchimento da Receita Federal
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"], input[name*="name"]').first();
    await expect(razaoSocialInput).toHaveValue(/BRAZIL HOME CARE|BRASIL HOME CARE/i, { timeout: 10000 });

    const nomeFantasiaInput = page.locator('input[placeholder*="Nome Fantasia"], input[name*="trade_name"]').first();
    await expect(nomeFantasiaInput).toHaveValue(/DOMICILE|DOMICILIO/i, { timeout: 5000 });

    // Preencher CEP válido
    const cepInput = page.locator('input[placeholder*="CEP"], input[name*="zip_code"]').first();
    await cepInput.fill('13201840'); // CEP real de Jundiaí

    // Aguardar consulta automática do ViaCEP
    await page.waitForTimeout(2000);

    // Verificar auto-preenchimento do ViaCEP
    const logradouroInput = page.locator('input[placeholder*="logradouro"], input[name*="street"]').first();
    await expect(logradouroInput).toHaveValue(/RUA|AVENIDA/i, { timeout: 5000 });

    const bairroInput = page.locator('input[placeholder*="bairro"], input[name*="neighborhood"]').first();
    await expect(bairroInput).not.toBeEmpty();

    const cidadeInput = page.locator('input[placeholder*="cidade"], input[name*="city"]').first();
    await expect(cidadeInput).toHaveValue(/JUNDIAI|JUNDIÁI/i, { timeout: 5000 });

    const estadoInput = page.locator('select[name*="state"], input[name*="state"]').first();
    await expect(estadoInput).toHaveValue('SP');

    // Preencher telefone
    const telefoneInput = page.locator('input[placeholder*="telefone"], input[name*="phones"]').first();
    await telefoneInput.fill('11999999999');

    // Preencher email
    const emailInput = page.locator('input[type="email"], input[name*="emails"]').first();
    await emailInput.fill('contato@empresa-teste.com.br');

    // Verificar se coordenadas foram adicionadas (geocoding)
    // Nota: Isso pode não ser visível na UI, mas podemos verificar via network requests

    // Submeter formulário
    const submitButton = page.locator('button[type="submit"], button:has-text("Salvar"), button:has-text("Cadastrar")').first();
    await submitButton.click();

    // Aguardar processamento e redirecionamento
    await page.waitForTimeout(3000);

    // Verificar sucesso - pode redirecionar para listagem ou detalhes
    await expect(page).toHaveURL(/.*empresas.*/, { timeout: 10000 });

    // Verificar mensagem de sucesso
    await expect(page.locator('text=/sucesso|criada|salva/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve cadastrar empresa com CNPJ válido mas CEP inválido', async ({ page }) => {
    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher CNPJ válido
    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('05.514.464/0001-30');

    // Aguardar Receita Federal
    await page.waitForTimeout(3000);
    await expect(page.locator('input[placeholder*="Razão Social"]').first()).toHaveValue(/BRAZIL HOME CARE/i);

    // Preencher CEP inválido
    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill('99999999');

    // Aguardar tentativa de ViaCEP (deve falhar)
    await page.waitForTimeout(2000);

    // Verificar que campos de endereço permaneceram vazios ou com valores padrão
    const logradouroInput = page.locator('input[placeholder*="logradouro"]').first();
    await expect(logradouroInput).toBeEmpty();

    // Mas Receita Federal deve ter funcionado
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"]').first();
    await expect(razaoSocialInput).not.toBeEmpty();

    // Completar cadastro mínimo
    const telefoneInput = page.locator('input[placeholder*="telefone"]').first();
    await telefoneInput.fill('11999999999');

    const emailInput = page.locator('input[type="email"]').first();
    await emailInput.fill('teste@empresa.com.br');

    // Submeter
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Deve funcionar mesmo com enriquecimento parcial
    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve cadastrar empresa com dados manuais (sem enriquecimento)', async ({ page }) => {
    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher todos os dados manualmente (sem CNPJ/CEP que triggeram APIs)
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"]').first();
    await razaoSocialInput.fill('Empresa Manual LTDA');

    const nomeFantasiaInput = page.locator('input[placeholder*="Nome Fantasia"]').first();
    await nomeFantasiaInput.fill('Empresa Manual');

    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('99.999.999/0001-99'); // CNPJ que não existe na Receita

    // Preencher endereço manual
    const logradouroInput = page.locator('input[placeholder*="logradouro"]').first();
    await logradouroInput.fill('Rua Manual');

    const numeroInput = page.locator('input[placeholder*="número"]').first();
    await numeroInput.fill('123');

    const bairroInput = page.locator('input[placeholder*="bairro"]').first();
    await bairroInput.fill('Centro');

    const cidadeInput = page.locator('input[placeholder*="cidade"]').first();
    await cidadeInput.fill('São Paulo');

    const estadoInput = page.locator('select[name*="state"]').first();
    await estadoInput.selectOption('SP');

    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill('99999999'); // CEP inválido

    // Contatos
    const telefoneInput = page.locator('input[placeholder*="telefone"]').first();
    await telefoneInput.fill('11999999999');

    const emailInput = page.locator('input[type="email"]').first();
    await emailInput.fill('manual@empresa.com.br');

    // Submeter
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Deve funcionar com dados manuais
    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve validar CNPJ duplicado durante cadastro', async ({ page }) => {
    // Primeiro, cadastrar uma empresa
    await page.goto('/admin/empresas?view=create');

    const cnpjInput1 = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput1.fill('11.222.333/0001-44');

    const razaoSocialInput1 = page.locator('input[placeholder*="Razão Social"]').first();
    await razaoSocialInput1.fill('Empresa Original LTDA');

    const telefoneInput1 = page.locator('input[placeholder*="telefone"]').first();
    await telefoneInput1.fill('11999999999');

    const emailInput1 = page.locator('input[type="email"]').first();
    await emailInput1.fill('original@empresa.com.br');

    const submitButton1 = page.locator('button[type="submit"]').first();
    await submitButton1.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });

    // Agora tentar cadastrar outra empresa com o mesmo CNPJ
    await page.goto('/admin/empresas?view=create');

    const cnpjInput2 = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput2.fill('11.222.333/0001-44'); // Mesmo CNPJ

    // Aguardar validação
    await page.waitForTimeout(2000);

    // Deve mostrar erro de CNPJ duplicado
    await expect(page.locator('text=/duplicado|já existe|já cadastrado/i')).toBeVisible({ timeout: 5000 });

    // Botão de submit deve estar desabilitado
    const submitButton2 = page.locator('button[type="submit"]').first();
    await expect(submitButton2).toBeDisabled();
  });

  test('deve lidar com falha temporária das APIs externas', async ({ page }) => {
    // Simular falha nas APIs externas
    await page.route('https://receitaws.com.br/**', route => route.abort());
    await page.route('https://viacep.com.br/**', route => route.abort());

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher dados básicos
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"]').first();
    await razaoSocialInput.fill('Empresa Offline LTDA');

    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('88.888.888/0001-88');

    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill('88888888');

    // Aguardar tentativas de API (devem falhar)
    await page.waitForTimeout(3000);

    // Sistema deve continuar funcionando
    const telefoneInput = page.locator('input[placeholder*="telefone"]').first();
    await telefoneInput.fill('11999999999');

    const emailInput = page.locator('input[type="email"]').first();
    await emailInput.fill('offline@empresa.com.br');

    // Submeter deve funcionar mesmo com APIs offline
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });
});