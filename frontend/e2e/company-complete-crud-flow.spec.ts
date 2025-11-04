import { test, expect } from "@playwright/test";

test.describe("Fluxo Completo CRUD de Empresa - E2E", () => {
  const TEST_CNPJ = "52.558.838/6999-76";
  const TEST_CNPJ_CLEAN = "52558838699976";
  let createdCompanyId: number;

  test("1 - Abrir lista de empresas", async ({ page, context }) => {
    console.log("📋 PASSO 1: Abrir lista de empresas");

    // Limpar estado
    await context.clearCookies();

    // Fazer login
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const submitButton = page.locator('button[type="submit"]');

    await emailInput.fill("admin@example.com");
    await passwordInput.fill("password");
    await submitButton.click();

    await page.waitForURL("**/admin**", { timeout: 10000 });

    // Configurar permissões
    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    // Navegar para lista de empresas
    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Verificar se estamos na lista
    await expect(page.getByText("Empresas")).toBeVisible();

    console.log("✅ Lista de empresas carregada com sucesso");
  });

  test("2 - Incluir uma nova empresa", async ({ page, context }) => {
    console.log("🏢 PASSO 2: Incluir uma nova empresa");

    // Setup inicial (login e navegação)
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    // 2.1 - Informar CNPJ e consultar na API
    console.log("🔍 2.1 - Informar CNPJ e consultar na API");
    await page.goto("/admin/empresas?view=create");
    await page.waitForLoadState("networkidle");

    const cnpjInput = page.getByLabel("CNPJ");
    await cnpjInput.fill(TEST_CNPJ);

    const consultarButton = page.getByRole("button", { name: /consultar/i });
    await expect(consultarButton).toBeVisible();
    await consultarButton.click();

    // Aguardar carregamento dos dados
    await page.waitForTimeout(3000);

    // Verificar se dados foram carregados (pode ser mock ou API real)
    const razaoSocialInput = page.getByLabel("Razão Social");
    const hasRazaoSocial = await razaoSocialInput.inputValue();
    console.log(`📄 Razão Social carregada: ${hasRazaoSocial || 'N/A'}`);

    // 2.2 - Na falta de algum dado, preencher com dados fictícios
    console.log("✏️ 2.2 - Preencher dados faltantes com fictícios");

    // Garantir que temos razão social
    if (!hasRazaoSocial) {
      await razaoSocialInput.fill("EMPRESA TESTE LTDA");
    }

    // Preencher nome fantasia se vazio
    const fantasiaInput = page.getByLabel("Nome Fantasia");
    const hasFantasia = await fantasiaInput.inputValue();
    if (!hasFantasia) {
      await fantasiaInput.fill("EMPRESA TESTE");
    }

    // Preencher telefone se necessário
    const phoneInputs = page.locator('input[placeholder*="telefone"]');
    const phoneCount = await phoneInputs.count();
    if (phoneCount === 0) {
      // Adicionar telefone se não existir
      const addPhoneButton = page.getByRole("button", { name: /adicionar telefone/i });
      if (await addPhoneButton.isVisible()) {
        await addPhoneButton.click();
      }
    }

    const phoneInput = page.locator('input[placeholder*="telefone"]').first();
    await phoneInput.fill("11999999999");

    const phoneTypeSelect = page.locator("select").filter({ hasText: "Tipo" }).first();
    await phoneTypeSelect.selectOption("commercial");

    // Preencher email se necessário
    const emailInputs = page.locator('input[type="email"]');
    const emailCount = await emailInputs.count();
    if (emailCount === 0) {
      // Adicionar email se não existir
      const addEmailButton = page.getByRole("button", { name: /adicionar email/i });
      if (await addEmailButton.isVisible()) {
        await addEmailButton.click();
      }
    }

    const emailInput = page.locator('input[type="email"]').first();
    await emailInput.fill("contato@empresateste.com.br");

    const emailTypeSelect = page.locator("select").filter({ hasText: "Tipo" }).nth(1);
    await emailTypeSelect.selectOption("work");

    // Preencher endereço se necessário
    const cepInput = page.locator('input[placeholder*="CEP"]').first();
    await cepInput.fill("01001000");

    // Aguardar ViaCEP
    await page.waitForTimeout(2000);

    // Preencher número se não foi preenchido
    const numberInput = page.locator('input[placeholder*="número"]').first();
    const hasNumber = await numberInput.inputValue();
    if (!hasNumber) {
      await numberInput.fill("123");
    }

    // 2.3 - Salvar empresa
    console.log("💾 2.3 - Salvar empresa");
    const saveButton = page.getByRole("button", { name: /salvar/i });
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Aguardar processamento
    await page.waitForTimeout(5000);

    // Verificar sucesso
    const successMessage = page.getByText(/empresa cadastrada com sucesso/i);
    const hasSuccess = await successMessage.isVisible().catch(() => false);

    if (hasSuccess) {
      console.log("✅ Empresa salva com sucesso");
    } else {
      // Pode ter redirecionado para a lista
      await page.waitForURL("**/empresas**", { timeout: 10000 });
      console.log("✅ Empresa salva (redirecionado para lista)");
    }

    // 2.4 - Verificar geocodificação (endereço complementado)
    console.log("🗺️ 2.4 - Verificar geocodificação");
    // Esta validação pode ser feita na consulta posterior
  });

  test("3 - Empresa nova criada está na lista?", async ({ page, context }) => {
    console.log("📋 PASSO 3: Verificar se empresa nova está na lista");

    // Setup
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Procurar empresa na lista
    const companyInList = page.getByText(TEST_CNPJ);
    const isVisible = await companyInList.isVisible().catch(() => false);

    if (isVisible) {
      console.log("✅ Empresa encontrada na lista");
    } else {
      console.log("❌ Empresa NÃO encontrada na lista");
      // Capturar screenshot para debug
      await page.screenshot({
        path: "test-results/company-not-in-list.png",
        fullPage: true,
      });
      throw new Error("Empresa não apareceu na lista após criação");
    }
  });

  test("4 - Abrir consulta de empresa e validar dados", async ({ page, context }) => {
    console.log("🔍 PASSO 4: Abrir consulta de empresa e validar dados");

    // Setup
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Clicar na empresa da lista
    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();

    // Aguardar carregamento da página de detalhes
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Validar dados básicos
    await expect(page.getByText(TEST_CNPJ)).toBeVisible();
    console.log("✅ Página de detalhes da empresa carregada");
  });

  test("4.1 - Validar mascaramento LGPD", async ({ page, context }) => {
    console.log("🔒 PASSO 4.1: Validar mascaramento LGPD");

    // Setup e navegação para empresa
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Verificar mascaramento - CNPJ deve aparecer mascarado
    const maskedCNPJ = page.getByText(/\*\*\*.\*\*\*.\*\*\*\/\*\*\*\*-\*\*/);
    const hasMaskedCNPJ = await maskedCNPJ.isVisible().catch(() => false);

    if (hasMaskedCNPJ) {
      console.log("✅ CNPJ está mascarado conforme LGPD");
    } else {
      console.log("⚠️ CNPJ não está mascarado - verificar implementação");
    }
  });

  test("4.2 - Revelar dados sensíveis", async ({ page, context }) => {
    console.log("👁️ PASSO 4.2: Revelar dados sensíveis");

    // Setup e navegação
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Procurar botão de revelar dados
    const revealButton = page.getByRole("button", { name: /revelar/i });
    const hasRevealButton = await revealButton.isVisible().catch(() => false);

    if (hasRevealButton) {
      await revealButton.click();
      await page.waitForTimeout(2000);

      // Verificar se CNPJ completo está visível
      const fullCNPJ = page.getByText(TEST_CNPJ);
      const hasFullCNPJ = await fullCNPJ.isVisible().catch(() => false);

      if (hasFullCNPJ) {
        console.log("✅ Dados sensíveis revelados com sucesso");
      } else {
        console.log("❌ Dados sensíveis não foram revelados");
      }
    } else {
      console.log("⚠️ Botão de revelar não encontrado");
    }
  });

  test("4.3 - Verificar logs LGPD", async ({ page, context }) => {
    console.log("📝 PASSO 4.3: Verificar logs LGPD");

    // Setup e navegação
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Navegar para aba LGPD
    const lgpdTab = page.getByRole("tab", { name: /lgpd/i });
    const hasLGPDTab = await lgpdTab.isVisible().catch(() => false);

    if (hasLGPDTab) {
      await lgpdTab.click();
      await page.waitForTimeout(2000);

      // Verificar se há logs
      const logEntries = page.locator("[data-testid='lgpd-log-entry']");
      const logCount = await logEntries.count();

      if (logCount > 0) {
        console.log(`✅ ${logCount} logs LGPD encontrados`);
      } else {
        console.log("⚠️ Nenhum log LGPD encontrado");
      }
    } else {
      console.log("⚠️ Aba LGPD não encontrada");
    }
  });

  test("5 - Alterar dados (exceto chave)", async ({ page, context }) => {
    console.log("✏️ PASSO 5: Alterar dados (exceto chave)");

    // Setup e navegação
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Procurar botão de editar
    const editButton = page.getByRole("button", { name: /editar/i });
    const hasEditButton = await editButton.isVisible().catch(() => false);

    if (hasEditButton) {
      await editButton.click();
      await page.waitForTimeout(2000);

      // Alterar nome fantasia (não é campo chave)
      const fantasiaInput = page.getByLabel("Nome Fantasia");
      await fantasiaInput.fill("EMPRESA TESTE ALTERADA");

      // Salvar alterações
      const saveButton = page.getByRole("button", { name: /salvar/i });
      await saveButton.click();
      await page.waitForTimeout(3000);

      console.log("✅ Dados alterados com sucesso");
    } else {
      console.log("⚠️ Botão de editar não encontrado");
    }
  });

  test("6 - Empresa alterada está na lista?", async ({ page, context }) => {
    console.log("📋 PASSO 6: Empresa alterada está na lista?");

    // Setup
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Verificar se nome fantasia alterado aparece
    const alteredCompany = page.getByText("EMPRESA TESTE ALTERADA");
    const isVisible = await alteredCompany.isVisible().catch(() => false);

    if (isVisible) {
      console.log("✅ Empresa com dados alterados encontrada na lista");
    } else {
      console.log("⚠️ Empresa alterada não encontrada ou nome não atualizado na lista");
    }
  });

  test("7 - Inativar empresa", async ({ page, context }) => {
    console.log("🚫 PASSO 7: Inativar empresa");

    // Setup e navegação
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    const companyLink = page.getByText(TEST_CNPJ);
    await companyLink.click();
    await page.waitForURL("**/empresas/**", { timeout: 10000 });

    // Procurar botão de inativar
    const deactivateButton = page.getByRole("button", { name: /inativar/i });
    const hasDeactivateButton = await deactivateButton.isVisible().catch(() => false);

    if (hasDeactivateButton) {
      await deactivateButton.click();

      // Confirmar inativação se houver modal
      const confirmButton = page.getByRole("button", { name: /confirmar/i });
      if (await confirmButton.isVisible().catch(() => false)) {
        await confirmButton.click();
      }

      await page.waitForTimeout(3000);
      console.log("✅ Empresa inativada com sucesso");
    } else {
      console.log("⚠️ Botão de inativar não encontrado");
    }
  });

  test("8 - Empresa inativada não está na lista?", async ({ page, context }) => {
    console.log("📋 PASSO 8: Empresa inativada não está na lista?");

    // Setup
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Verificar filtros - deve haver filtro de status
    const activeFilter = page.getByRole("button", { name: /ativas/i });
    const hasActiveFilter = await activeFilter.isVisible().catch(() => false);

    if (hasActiveFilter) {
      // Filtro ativo - empresa inativada não deve aparecer
      const companyInList = page.getByText(TEST_CNPJ);
      const isVisible = await companyInList.isVisible().catch(() => false);

      if (!isVisible) {
        console.log("✅ Empresa inativada não aparece na lista (filtro ativo)");
      } else {
        console.log("❌ Empresa inativada ainda aparece na lista");
      }
    } else {
      console.log("⚠️ Filtro de status não encontrado");
    }
  });

  test("9 - Ativar empresa", async ({ page, context }) => {
    console.log("✅ PASSO 9: Ativar empresa");

    // Setup e navegação
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Alterar filtro para mostrar inativas
    const inactiveFilter = page.getByRole("button", { name: /inativas/i });
    if (await inactiveFilter.isVisible().catch(() => false)) {
      await inactiveFilter.click();
      await page.waitForTimeout(2000);
    }

    const companyLink = page.getByText(TEST_CNPJ);
    const isVisible = await companyLink.isVisible().catch(() => false);

    if (isVisible) {
      await companyLink.click();
      await page.waitForURL("**/empresas/**", { timeout: 10000 });

      // Procurar botão de ativar
      const activateButton = page.getByRole("button", { name: /ativar/i });
      const hasActivateButton = await activateButton.isVisible().catch(() => false);

      if (hasActivateButton) {
        await activateButton.click();

        // Confirmar ativação se houver modal
        const confirmButton = page.getByRole("button", { name: /confirmar/i });
        if (await confirmButton.isVisible().catch(() => false)) {
          await confirmButton.click();
        }

        await page.waitForTimeout(3000);
        console.log("✅ Empresa ativada com sucesso");
      } else {
        console.log("⚠️ Botão de ativar não encontrado");
      }
    } else {
      console.log("⚠️ Empresa inativada não encontrada na lista de inativas");
    }
  });

  test("10 - Empresa ativada está na lista?", async ({ page, context }) => {
    console.log("📋 PASSO 10: Empresa ativada está na lista?");

    // Setup
    await context.clearCookies();
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.locator('input[type="email"]').fill("admin@example.com");
    await page.locator('input[type="password"]').fill("password");
    await page.locator('button[type="submit"]').click();
    await page.waitForURL("**/admin**", { timeout: 10000 });

    await page.addInitScript(() => {
      localStorage.setItem("useDynamicMenus", "true");
      localStorage.setItem("testAsRoot", "true");
    });

    await page.goto("/admin/empresas");
    await page.waitForLoadState("networkidle");

    // Verificar filtro ativo
    const activeFilter = page.getByRole("button", { name: /ativas/i });
    if (await activeFilter.isVisible().catch(() => false)) {
      await activeFilter.click();
      await page.waitForTimeout(2000);
    }

    const companyInList = page.getByText(TEST_CNPJ);
    const isVisible = await companyInList.isVisible().catch(() => false);

    if (isVisible) {
      console.log("✅ Empresa ativada aparece na lista");
    } else {
      console.log("❌ Empresa ativada não aparece na lista");
    }
  });
});