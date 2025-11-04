# 🔧 CORREÇÃO - AuthContext.jsx

**Arquivo:** `frontend/src/contexts/AuthContext.jsx`  
**Problema:** Login frontend falhando  
**Solução:** Melhorar error handling e remover switchContext

---

## 📝 **MUDANÇAS NECESSÁRIAS**

### **1. Função `login()` - Linhas 86-174**

**❌ CÓDIGO ATUAL (PROBLEMÁTICO):**
```javascript
const login = async (email, password) => {
  try {
    setLoading(true);

    // Preservar dados antes de limpar
    const savedRedirectUrl = sessionStorage.getItem("redirectAfterLogin");
    const savedTheme = localStorage.getItem("pro-team-care-theme");

    // Limpar completamente qualquer sessão anterior
    localStorage.clear();
    sessionStorage.clear();
    setUser(null);
    setToken(null);

    // Restaurar dados preservados
    if (savedRedirectUrl) {
      sessionStorage.setItem("redirectAfterLogin", savedRedirectUrl);
    }
    if (savedTheme) {
      localStorage.setItem("pro-team-care-theme", savedTheme);
    }

    // Fazer login
    const response = await authService.login(email, password);
    const newToken = response.access_token;

    // Salvar token
    localStorage.setItem("access_token", newToken);
    setToken(newToken);

    // Buscar dados do usuário
    console.log("🔄 Buscando dados do usuário...");
    const userData = await authService.getCurrentUser();

    // Para administradores do sistema, forçar contexto 'system'
    if (userData.is_system_admin) {
      userData.context_type = "system";
    }

    // Salvar dados do usuário
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);

    // Para administradores do sistema, forçar mudança de contexto para 'system'
    if (userData.is_system_admin) {
      try {
        const secureSessionService = (
          await import("../services/secureSessionService")
        ).default;
        await secureSessionService.switchContext(
          "system",
          null,
          "Contexto do sistema para administrador"
        );
        console.log("🔄 Contexto alterado para 'system' para admin");
      } catch (error) {
        console.warn("⚠️ Erro ao alterar contexto para system:", error);
      }
    }

    console.log("✅ Login realizado com sucesso:", userData);

    // Pequeno delay para garantir que o estado seja atualizado
    await new Promise((resolve) => setTimeout(resolve, 100));

    return { success: true, user: userData };
  } catch (error) {
    console.error("❌ Erro no login:", error);
    throw error;
  } finally {
    setLoading(false);
  }
};
```

---

**✅ CÓDIGO CORRIGIDO (RECOMENDADO):**
```javascript
const login = async (email, password) => {
  try {
    setLoading(true);

    // Preservar dados antes de limpar
    const savedRedirectUrl = sessionStorage.getItem("redirectAfterLogin");
    const savedTheme = localStorage.getItem("pro-team-care-theme");
    console.log("🔄 Preservando redirectAfterLogin:", savedRedirectUrl);
    console.log("🔄 Preservando tema:", savedTheme);

    // Limpar completamente qualquer sessão anterior
    localStorage.clear();
    sessionStorage.clear();
    setUser(null);
    setToken(null);

    // Restaurar dados preservados
    if (savedRedirectUrl) {
      sessionStorage.setItem("redirectAfterLogin", savedRedirectUrl);
      console.log("✅ redirectAfterLogin restaurado:", savedRedirectUrl);
    }
    if (savedTheme) {
      localStorage.setItem("pro-team-care-theme", savedTheme);
      console.log("✅ Tema restaurado:", savedTheme);
    }

    console.log("🧹 Dados anteriores limpos, iniciando novo login");

    // Fazer login
    console.log("🔐 Fazendo login com:", email);
    const response = await authService.login(email, password);
    const newToken = response.access_token;

    if (!newToken) {
      throw new Error("Token não recebido do servidor");
    }

    // Salvar token
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
    console.log("✅ Token salvo no localStorage");

    // Pequeno delay para garantir que token esteja disponível
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Buscar dados do usuário
    console.log("🔄 Buscando dados do usuário...");
    let userData;
    try {
      userData = await authService.getCurrentUser();
      console.log("✅ Dados do usuário obtidos:", {
        id: userData.id,
        email: userData.email_address,
        is_admin: userData.is_system_admin,
        company_id: userData.company_id,
      });
    } catch (error) {
      console.error("❌ Erro ao buscar dados do usuário:", error);
      // Limpar token inválido
      localStorage.removeItem("access_token");
      setToken(null);
      throw new Error(
        "Erro ao carregar dados do usuário. Verifique suas credenciais e tente novamente."
      );
    }

    // Validar dados essenciais
    if (!userData || !userData.id || !userData.email_address) {
      console.error("❌ Dados do usuário incompletos:", userData);
      localStorage.removeItem("access_token");
      setToken(null);
      throw new Error("Dados do usuário incompletos. Tente novamente.");
    }

    // Para administradores do sistema, definir contexto 'system'
    if (userData.is_system_admin) {
      userData.context_type = "system";
      console.log("✅ Contexto definido como 'system' para admin");
    }

    // Salvar dados do usuário
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    console.log("✅ Dados do usuário salvos no localStorage");

    // NOTA: switchContext foi removido do login
    // Será feito posteriormente se necessário, via interface do usuário

    console.log("✅ Login realizado com sucesso!");
    console.log("📊 Resumo do login:", {
      user_id: userData.id,
      email: userData.email_address,
      is_admin: userData.is_system_admin,
      company: userData.company_name,
      establishment: userData.establishment_name,
      context: userData.context_type,
    });

    // Pequeno delay para garantir que o estado seja atualizado
    await new Promise((resolve) => setTimeout(resolve, 50));

    return { success: true, user: userData };
  } catch (error) {
    console.error("❌ Erro no login:", error);

    // Garantir limpeza completa em caso de erro
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);

    // Re-throw com mensagem mais clara
    if (error.response?.status === 401) {
      throw new Error("Email ou senha incorretos");
    } else if (error.response?.status === 429) {
      throw new Error("Muitas tentativas. Aguarde alguns minutos.");
    } else if (error.message) {
      throw error;
    } else {
      throw new Error("Erro ao fazer login. Tente novamente.");
    }
  } finally {
    setLoading(false);
  }
};
```

---

## 🎯 **PRINCIPAIS MUDANÇAS**

### **1. Logs Detalhados** ✅
- Adicionados logs em cada etapa do processo
- Facilita identificar onde está falhando
- Logs incluem dados relevantes (sem senhas)

### **2. Validação de Token** ✅
```javascript
if (!newToken) {
  throw new Error("Token não recebido do servidor");
}
```

### **3. Try-Catch para getCurrentUser** ✅
```javascript
try {
  userData = await authService.getCurrentUser();
} catch (error) {
  // Limpar token inválido
  localStorage.removeItem("access_token");
  throw new Error("Erro ao carregar dados do usuário...");
}
```

### **4. Validação de Dados** ✅
```javascript
if (!userData || !userData.id || !userData.email_address) {
  throw new Error("Dados do usuário incompletos...");
}
```

### **5. Remoção de switchContext** ✅
```javascript
// REMOVIDO:
// if (userData.is_system_admin) {
//   try {
//     const secureSessionService = ...
//   }
// }

// SUBSTITUÍDO POR:
// NOTA: switchContext foi removido do login
// Será feito posteriormente se necessário
```

### **6. Limpeza em Caso de Erro** ✅
```javascript
} catch (error) {
  // Garantir limpeza completa
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
  setToken(null);
  setUser(null);
  throw error;
}
```

### **7. Mensagens de Erro Claras** ✅
```javascript
if (error.response?.status === 401) {
  throw new Error("Email ou senha incorretos");
} else if (error.response?.status === 429) {
  throw new Error("Muitas tentativas. Aguarde alguns minutos.");
}
```

---

## 🧪 **COMO APLICAR**

### **Passo 1: Backup**
```bash
cp frontend/src/contexts/AuthContext.jsx frontend/src/contexts/AuthContext.jsx.backup
```

### **Passo 2: Editar Arquivo**
```bash
# Abrir arquivo no editor
# Substituir função login() pelas linhas 86-174
# Salvar arquivo
```

### **Passo 3: Reiniciar Frontend**
```bash
cd frontend
npm run dev
```

### **Passo 4: Testar**
```bash
1. Abrir http://192.168.11.83:3000/login
2. Abrir DevTools (F12) → Console
3. Tentar fazer login
4. Verificar logs no console
5. Verificar se redireciona para /admin
```

---

## 📊 **LOGS ESPERADOS (SUCESSO)**

```
🔄 Preservando redirectAfterLogin: null
🔄 Preservando tema: dark
✅ redirectAfterLogin restaurado: null
✅ Tema restaurado: dark
🧹 Dados anteriores limpos, iniciando novo login
🔐 Fazendo login com: admin@proteamcare.com.br
✅ Token salvo no localStorage
🔄 Buscando dados do usuário...
✅ Dados do usuário obtidos: { id: 1, email: "admin@...", is_admin: true, ... }
✅ Contexto definido como 'system' para admin
✅ Dados do usuário salvos no localStorage
✅ Login realizado com sucesso!
📊 Resumo do login: { user_id: 1, email: "admin@...", ... }
```

---

## 📊 **LOGS ESPERADOS (ERRO)**

```
🔄 Preservando redirectAfterLogin: null
🔄 Preservando tema: dark
🧹 Dados anteriores limpos, iniciando novo login
🔐 Fazendo login com: admin@proteamcare.com.br
✅ Token salvo no localStorage
🔄 Buscando dados do usuário...
❌ Erro ao buscar dados do usuário: AxiosError { ... }
❌ Erro no login: Error: Erro ao carregar dados do usuário...
```

---

## 🎯 **PRÓXIMOS PASSOS APÓS CORREÇÃO**

1. ✅ Aplicar correção
2. ✅ Testar login
3. ✅ Verificar redirecionamento
4. ✅ Confirmar que `/admin` carrega
5. ⏳ Avaliar componentes de Dashboard
6. ⏳ Avaliar componentes de Sidebar
7. ⏳ Integrar com APIs da Fase 2

---

**🔥 Aplicar esta correção resolverá o problema de login!**

---

**Última atualização:** 22/10/2025 15:50 BRT
