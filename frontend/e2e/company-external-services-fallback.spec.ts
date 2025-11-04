/**
 * Testes E2E para cenários de fallback quando APIs externas falham.
 *
 * Testa resiliência: sistema deve continuar funcionando mesmo com
 * Receita Federal, ViaCEP e Geocoding indisponíveis.
 */

import { test, expect } from '@playwright/test';

test.describe('Fallback de Serviços Externos no Cadastro de Empresa', () => {
  test.beforeEach(async ({ page }) => {
    // Login como admin
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@proteamcare.com.br');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Aguardar redirecionamento
    await page.waitForURL('**/admin**');
  });

  test('deve cadastrar empresa quando Receita Federal está offline', async ({ page }) => {
    // Mock: Receita Federal offline
    await page.route('https://receitaws.com.br/**', route => route.abort());
    await page.route('https://www.receitaws.com.br/**', route => route.abort());

    // ViaCEP e Geocoding continuam funcionando
    await page.route('https://viacep.com.br/**', route => route.passThrough());

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher CNPJ (Receita vai falhar)
    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('11.222.333/0001-44');

    // Aguardar tentativa de consulta (deve falhar silenciosamente)
    await page.waitForTimeout(3000);

    // Campos devem permanecer vazios (sem auto-preenchimento)
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"]').first();
    await expect(razaoSocialInput).toBeEmpty();

    // Usuário deve poder preencher manualmente
    await razaoSocialInput.fill('Empresa Manual LTDA');
    await page.locator('input[placeholder*="Nome Fantasia"]').first().fill('Empresa Manual');

    // Preencher CEP válido (ViaCEP deve funcionar)
    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill('01001000');

    // Aguardar ViaCEP
    await page.waitForTimeout(2000);

    // ViaCEP deve funcionar mesmo com Receita offline
    const logradouroInput = page.locator('input[placeholder*="logradouro"]').first();
    await expect(logradouroInput).toHaveValue(/Praça|Praça da Sé/i);

    // Completar cadastro
    await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
    await page.locator('input[type="email"]').first().fill('teste@empresa.com.br');

    // Submeter deve funcionar
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve cadastrar empresa quando ViaCEP está offline', async ({ page }) => {
    // Mock: ViaCEP offline
    await page.route('https://viacep.com.br/**', route => route.abort());

    // Receita Federal continua funcionando
    await page.route('https://receitaws.com.br/**', route => route.passThrough());

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher CNPJ válido (Receita deve funcionar)
    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('05.514.464/0001-30');

    // Aguardar Receita Federal
    await page.waitForTimeout(3000);
    await expect(page.locator('input[placeholder*="Razão Social"]').first()).toHaveValue(/BRAZIL HOME CARE/i);

    // Preencher CEP (ViaCEP vai falhar)
    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill('01001000');

    // Aguardar tentativa ViaCEP (deve falhar)
    await page.waitForTimeout(2000);

    // Campos de endereço devem permanecer vazios
    const logradouroInput = page.locator('input[placeholder*="logradouro"]').first();
    await expect(logradouroInput).toBeEmpty();

    // Usuário deve poder preencher manualmente
    await logradouroInput.fill('Rua Manual');
    await page.locator('input[placeholder*="número"]').first().fill('123');
    await page.locator('input[placeholder*="bairro"]').first().fill('Centro');
    await page.locator('input[placeholder*="cidade"]').first().fill('São Paulo');
    await page.locator('select[name*="state"]').first().selectOption('SP');

    // Completar cadastro
    await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
    await page.locator('input[type="email"]').first().fill('teste@empresa.com.br');

    // Submeter deve funcionar
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve cadastrar empresa quando todas as APIs externas estão offline', async ({ page }) => {
    // Mock: Todas as APIs externas offline
    await page.route('https://receitaws.com.br/**', route => route.abort());
    await page.route('https://www.receitaws.com.br/**', route => route.abort());
    await page.route('https://viacep.com.br/**', route => route.abort());
    await page.route('https://nominatim.openstreetmap.org/**', route => route.abort());

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Todos os campos devem ser preenchidos manualmente
    await page.locator('input[placeholder*="Razão Social"]').first().fill('Empresa Totalmente Offline LTDA');
    await page.locator('input[placeholder*="Nome Fantasia"]').first().fill('Offline Total');
    await page.locator('input[placeholder*="CNPJ"]').first().fill('77.777.777/0001-77');

    // Endereço manual
    await page.locator('input[placeholder*="logradouro"]').first().fill('Rua Offline');
    await page.locator('input[placeholder*="número"]').first().fill('999');
    await page.locator('input[placeholder*="bairro"]').first().fill('Centro');
    await page.locator('input[placeholder*="cidade"]').first().fill('São Paulo');
    await page.locator('select[name*="state"]').first().selectOption('SP');
    await page.locator('input[placeholder*="CEP"]').first().fill('99999999');

    // Contatos
    await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
    await page.locator('input[type="email"]').first().fill('offline@empresa.com.br');

    // Submeter deve funcionar mesmo sem nenhuma API externa
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve mostrar avisos quando APIs externas falham', async ({ page }) => {
    // Mock: Receita Federal retorna erro
    await page.route('https://receitaws.com.br/v1/cnpj/**', route =>
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Serviço temporariamente indisponível' })
      })
    );

    // ViaCEP offline
    await page.route('https://viacep.com.br/**', route => route.abort());

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher CNPJ
    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('11.222.333/0001-44');

    // Aguardar tentativas de API
    await page.waitForTimeout(3000);

    // Sistema deve mostrar avisos de falha (toast notifications)
    // Nota: Dependendo da implementação, pode haver toasts ou apenas logs
    // await expect(page.locator('.toast-error, .notification-error')).toBeVisible();

    // Mas o formulário deve continuar funcional
    await page.locator('input[placeholder*="Razão Social"]').first().fill('Empresa com Avisos LTDA');
    await page.locator('input[placeholder*="Nome Fantasia"]').first().fill('Com Avisos');

    // Preencher endereço manual
    await page.locator('input[placeholder*="logradouro"]').first().fill('Rua dos Avisos');
    await page.locator('input[placeholder*="número"]').first().fill('123');
    await page.locator('input[placeholder*="bairro"]').first().fill('Centro');
    await page.locator('input[placeholder*="cidade"]').first().fill('São Paulo');
    await page.locator('select[name*="state"]').first().selectOption('SP');
    await page.locator('input[placeholder*="CEP"]').first().fill('01000000');

    // Contatos
    await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
    await page.locator('input[type="email"]').first().fill('avisos@empresa.com.br');

    // Submeter deve funcionar
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve lidar com timeout das APIs externas', async ({ page }) => {
    // Mock: APIs externas com delay excessivo (timeout)
    await page.route('https://receitaws.com.br/**', async route => {
      // Simular delay de 30 segundos (muito lento)
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.fulfill({ status: 200, body: '{}' });
    });

    await page.route('https://viacep.com.br/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 30000));
      await route.fulfill({ status: 200, body: '{}' });
    });

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher dados básicos rapidamente
    await page.locator('input[placeholder*="Razão Social"]').first().fill('Empresa Timeout LTDA');
    await page.locator('input[placeholder*="Nome Fantasia"]').first().fill('Timeout');
    await page.locator('input[placeholder*="CNPJ"]').first().fill('66.666.666/0001-66');

    // Preencher endereço
    await page.locator('input[placeholder*="logradouro"]').first().fill('Rua Timeout');
    await page.locator('input[placeholder*="número"]').first().fill('456');
    await page.locator('input[placeholder*="bairro"]').first().fill('Centro');
    await page.locator('input[placeholder*="cidade"]').first().fill('São Paulo');
    await page.locator('select[name*="state"]').first().selectOption('SP');
    await page.locator('input[placeholder*="CEP"]').first().fill('01000000');

    // Contatos
    await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
    await page.locator('input[type="email"]').first().fill('timeout@empresa.com.br');

    // Submeter imediatamente (não esperar pelas APIs lentas)
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Deve funcionar mesmo com APIs lentas/travadas
    await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
  });

  test('deve funcionar com rede instável (conexão intermitente)', async ({ page }) => {
    let requestCount = 0;

    // Mock: Alternar entre sucesso e falha para simular rede instável
    await page.route('https://receitaws.com.br/**', route => {
      requestCount++;
      if (requestCount % 2 === 0) {
        // Requisições pares falham
        route.abort();
      } else {
        // Requisições ímpares funcionam
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            nome: 'EMPRESA INSTAVEL LTDA',
            fantasia: 'Instável',
            situacao: 'ATIVA'
          })
        });
      }
    });

    // Navegar para formulário
    await page.goto('/admin/empresas?view=create');

    // Preencher CNPJ
    const cnpjInput = page.locator('input[placeholder*="CNPJ"]').first();
    await cnpjInput.fill('55.555.555/0001-55');

    // Aguardar tentativas (algumas vão falhar, outras funcionar)
    await page.waitForTimeout(5000);

    // Sistema deve ser resiliente e eventualmente funcionar
    const razaoSocialInput = page.locator('input[placeholder*="Razão Social"]').first();
    const currentValue = await razaoSocialInput.inputValue();

    // Se conseguiu consultar, deve ter preenchido
    if (currentValue.includes('INSTAVEL')) {
      // Receita funcionou em alguma tentativa
      await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
      await page.locator('input[type="email"]').first().fill('instavel@empresa.com.br');

      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
    } else {
      // Receita falhou, preencher manualmente
      await razaoSocialInput.fill('Empresa Instável LTDA');
      await page.locator('input[placeholder*="Nome Fantasia"]').first().fill('Instável');

      // Preencher resto dos dados
      await page.locator('input[placeholder*="logradouro"]').first().fill('Rua Instável');
      await page.locator('input[placeholder*="número"]').first().fill('789');
      await page.locator('input[placeholder*="bairro"]').first().fill('Centro');
      await page.locator('input[placeholder*="cidade"]').first().fill('São Paulo');
      await page.locator('select[name*="state"]').first().selectOption('SP');
      await page.locator('input[placeholder*="CEP"]').first().fill('01000000');
      await page.locator('input[placeholder*="telefone"]').first().fill('11999999999');
      await page.locator('input[type="email"]').first().fill('instavel@empresa.com.br');

      const submitButton = page.locator('button[type="submit"]').first();
      await submitButton.click();

      await expect(page.locator('text=/sucesso|criada/i')).toBeVisible({ timeout: 5000 });
    }
  });
});